import spinnaker_graph_front_end as sim
from pacman.model.constraints.placer_constraints import ChipAndCoreConstraint
from spinn_front_end_common.utility_models import \
    DataSpeedUpPacketGatherMachineVertex
from spinnaker_graph_front_end.examples import test_data_in_speed_up
from spinnaker_graph_front_end.examples.test_data_in_speed_up.\
    large_dsg_data_vertex import LargeDSGDataVertex
from spinn_front_end_common.utilities import globals_variables


class Runner(object):

    def __init__(self):
        pass

    def run(self, mbs, x, y):

        # setup system
        sim.setup(model_binary_module=test_data_in_speed_up,
                  n_chips_required=2)

        # build verts
        reader = LargeDSGDataVertex(mbs * 1024 * 1024)
        reader.add_constraint(ChipAndCoreConstraint(x=x, y=y))

        # add verts to graph
        sim.add_machine_vertex_instance(reader)

        sim.run(5)
        machine_graph = globals_variables.get_simulator()._mapping_outputs[
            "MemoryMachineGraph"]
        lpgmv = None
        for vertex in machine_graph.vertices:
            if isinstance(vertex, DataSpeedUpPacketGatherMachineVertex):
                lpgmv = vertex

        first = True
        speed = None
        missing_seq = None
        with open(lpgmv._data_in_report_path, "r") as reader:
            lines = reader.readlines()
            for line in lines[2:-1]:
                bits = line.split("\t\t")
                if int(bits[3]) == mbs * 1024 * 1024:
                    print "for {} bytes, mbs is {} with missing seqs " \
                          "of {}".format(mbs * 1024 * 1024, bits[5], bits[6])
                    speed = bits[5]
                    missing_seq = bits[6]

        sim.stop()
        return speed, missing_seq

if __name__ == "__main__":

    # entry point for doing speed search
    # data_sizes = [1, 2, 5, 10, 20, 30, 50]
    data_sizes = [1, 2, 5, 10, 20, 30, 50, 100]
    #locations = [(0, 0), (1, 1), (0, 3), (2, 4), (4, 0), (7, 7)]
    locations = [(1, 1), (0, 3), (2, 4), (4, 0), (7, 7)]
    iterations_per_type = 3
    runner = Runner()

    data_times = dict()
    overall_data_times = list()
    failed_to_run_states = list()
    lost_data_pattern = dict()

    for mbs_to_run in data_sizes:
        for x_coord, y_coord in locations:
            for iteration in range(0, iterations_per_type):
                print "###########################################" \
                      "###########################"
                print "running {}:{}:{}:{}".format(
                    mbs_to_run, x_coord, y_coord, iteration)
                print "##################################################" \
                      "####################"
                data_times[(mbs_to_run, x_coord, y_coord, iteration)] = \
                    runner.run(mbs_to_run, x_coord, y_coord)

    print data_times
