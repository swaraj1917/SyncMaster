# main.py
from problems import producer_consumer, dining_philosopher, reader_writer
from utils.control import SimulationControl


def main():
    print("Select a problem to run:")
    print("1. Producer-Consumer")
    print("2. Dining Philosophers")
    print("3. Reader-Writer")

    choice = input("Enter your choice (1/2/3): ")
    SimulationControl.init()

    if choice == '1':
        producer_consumer.run_simulation(
            buffer_size=5,
            num_producers=2,
            num_consumers=2,
            items_per_producer=5,
        )
    elif choice == '2':
        dining_philosopher.run_simulation(
            num_philosophers=5,
            eat_count=3,
            naive=False,
        )
    elif choice == '3':
        reader_writer.run_simulation(
            num_readers=3,
            num_writers=2,
            read_times=3,
            write_times=2,
        )
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()