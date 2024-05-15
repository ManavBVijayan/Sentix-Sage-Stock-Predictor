from django.views.decorators.cache import cache_control
from Data.models import StockPrice
from AdminDashBoard.models import ProcessLog
from django.shortcuts import render
import plotly.graph_objs as go
from datetime import timedelta,date


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):


    return render(request, 'home.html')

def explore(request):
    # Get the last 30 days of original closed prices
    last_30_days_prices = StockPrice.objects.order_by('-date')[:30]
    dates = [price.date.strftime('%Y-%m-%d') for price in last_30_days_prices]
    original_closed_prices = [price.close_price for price in last_30_days_prices]

    # Get the latest date available in the StockPrice model
    today = date.today()

    # Query the predicted values for the next 5 days
    try:
        process_log_entry = ProcessLog.objects.get(date=today)
        predicted_values = [getattr(process_log_entry, f"day{i}") for i in range(1, 6)]
    except ProcessLog.DoesNotExist:
        process_log_entry = None
        predicted_values = [None] * 5

    except ProcessLog.DoesNotExist:
        predicted_values = [None] * 5

    # Generate dates for the next 5 days
    next_5_days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 5)]

    # Create traces for original closed prices and predicted values
    trace_original = go.Scatter(x=dates, y=original_closed_prices, mode='lines', name='Closed Prices',
                                line=dict(color='blue',width=3),hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}')
    trace_predicted = go.Scatter(x=next_5_days, y=predicted_values, mode='lines', name='Predicted',
                                 line=dict(color='red',width=3),hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}')

    # Get the last original closed price and the first predicted value
    last_original_price = original_closed_prices[0]
    first_predicted_value = predicted_values[0]

    # Create a trace for the connection line
    trace_connection = go.Scatter(x=[dates[0], next_5_days[0]], y=[last_original_price, first_predicted_value],
                                  mode='lines', line=dict(color='red'), showlegend=False,hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}')

    # Query the previous predicted values for the last 30 days or less
    previous_predicted_values = []
    previous_dates = []
    i = 0
    while i < 30:
        prev_date = today - timedelta(days=i + 1)
        try:
            prev_process_log_entry = ProcessLog.objects.get(date=prev_date)
            previous_predicted_values.append(prev_process_log_entry.day1)
            previous_dates.append(prev_date.strftime('%Y-%m-%d'))
            print(f"Found data for {prev_date}: Day1 value = {prev_process_log_entry.day1}")
        except ProcessLog.DoesNotExist:
            print(f"No data found for {prev_date}")
        i += 1
    # Create trace for previous predicted values
    trace_previous_predicted = go.Scatter(x=previous_dates, y=previous_predicted_values, mode='markers',
                                          name='Previous', marker=dict(color='red', size=10),hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: %{y}')

    # Combine traces
    data = [trace_original, trace_predicted, trace_connection, trace_previous_predicted]

    layout = go.Layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        legend=dict(orientation="h", x=0, y=1.1),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='closest',
        plot_bgcolor='rgba(0, 0, 0, 0.7)',  # Adjust the opacity to make it darker
        height=600,  # Adjust height as needed
        width=900,  # Adjust width as needed
    )

    # Create figure
    fig = go.Figure(data=data, layout=layout)

    # Convert figure to JSON format
    graph_json = fig.to_json()

    # Render the HTML template with the graph JSON data
    return render(request, 'explore.html', {'graph_json': graph_json})