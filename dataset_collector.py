import csv
import os

class DatasetCollector:
    def __init__(self, filename: str='gestures_dataset.csv'):
        self.filename = filename
        self.recorded_counts = {0:0, 1:0, 2:0, 3:0}
        self._initialize_csv()


    def _initialize_csv(self):
        if not os.path.exists(self.filename):
            headers = []
            for i in range(21):
                headers.extend([f'lm{i}_x', f'lm{i}_y', f'lm{i}_z'])
            headers.append('label')

            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        else:
            # Load existing sample counts from CSV if file already exists
            with open(self.filename, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if row:
                        label = int(row[-1])
                        if label in self.recorded_counts:
                            self.recorded_counts[label] += 1

    """ save value and label of gesture"""
    def save_sample(self, features: list[float], label: int):
        if label not in self.recorded_counts:
            return

        row = features + [label]
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        self.recorded_counts[label]+=1

# Protect standalone execution
if __name__ == "__main__":
    collector = DatasetCollector()
    print("DatasetCollector Initialized. Current counts: ", collector.recorded_counts)