from optimizer.optimizer import Optimizer
from simulator.pps import PerPartnerSimulator
import pandas as pd

from simulator.simulator_core import SimulatorCore


class SimulatorStarter:
    def __init__(self, label_encoder, is_for_one_parnter=True, partner_id=None,
                 data_directory='../data/') -> None:
        self.is_for_one_partner = is_for_one_parnter
        self.data_dir = data_directory
        self.label_encoder = label_encoder
        if self.is_for_one_partner:
            self.partner_id = partner_id
        super().__init__()

    def start_simulation(self):
        if self.is_for_one_partner:
            simulator_core = SimulatorCore()
            optimizer = Optimizer(optimize_option='random', product_id_label_enc=self.label_encoder.get('product_id'))
            partner_df = pd.read_parquet(self.data_dir + "partners/partner_" + self.partner_id + ".parquet")
            per_partner_simulator = PerPartnerSimulator(partner_dataframe=partner_df, partner_id=self.partner_id,
                                                        optimizer=optimizer, simulator_core=simulator_core)
            per_partner_simulator.simulatePartner()
            per_partner_simulator.save_simulation_results(self.data_dir + "partner_performances/")
