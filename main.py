import pickle

from simulator.simulator_starter import SimulatorStarter

if __name__ == "__main__":
    labelEncoder = pickle.load(open("data/lablencoder.pickle", "rb"))
    simulation_starter = SimulatorStarter(label_encoder=labelEncoder, is_for_one_parnter=True, partner_id='235')
    simulation_starter.start_simulation()
