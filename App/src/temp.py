from datetime import datetime

# Get the current date
current_date = datetime.now()

# Format the date as "Month day, year"
formatted_date = current_date.strftime("%B %d, %Y")

# Print the formatted date
print(datetime.now().strftime("%B %d, %Y"))
