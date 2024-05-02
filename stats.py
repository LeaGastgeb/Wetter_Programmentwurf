import pandas as pd
import matplotlib.pyplot as plt


csv_file = 'example_stats_history.csv'

csv_data = pd.read_csv(csv_file)


# plt.figure(figsize=(10, 6))
# plt.plot(csv_data['User Count'], csv_data['Total Average Response Time'], color='green')
# #plt.plot(csv_data['User Count'], csv_data['Total Failure Count'], color='red')
# plt.xlabel('Anzahl der Benutzer')
# plt.ylabel('Antwortzeit in ms')
# plt.title('Antwortzeit in Abhängigkeit von der Anzahl der Benutzer')
# plt.legend()
# plt.show()

plt.figure(figsize=(10, 6))
plt.plot(csv_data['User Count'], csv_data['Total Request Count'], color='green')
plt.plot(csv_data['User Count'], csv_data['Total Failure Count'], color='red')
plt.xlabel('Anzahl der Benutzer')
plt.ylabel('Anzahl der Anfragen')
plt.title('Anzahl der Anfragen in Abhängigkeit von der Anzahl der Benutzer')
plt.legend()
plt.show()