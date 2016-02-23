# data spec imports
from spinn_storage_handlers.file_data_writer import FileDataWriter

# front end common imports
from spinn_front_end_common.utilities import exceptions

# general imports
from abc import ABCMeta
from six import add_metaclass
from abc import abstractmethod
import tempfile
import hashlib
import os


@add_metaclass(ABCMeta)
class AbstractPartitionedDataSpecableVertex(object):
    """ A vertex thats partitioned and needs data specification to occur
    """

    def __init__(self):
        self._no_machine_time_steps = None

    @abstractmethod
    def generate_data_spec(
            self, placement, sub_graph, routing_info, hostname, report_folder,
            ip_tags, reverse_ip_tags, write_text_specs,
            application_run_time_folder):
        """ Generate a data spec

        :param placement: the placement object for the dsg
        :param sub_graph: the partitioned graph object for this dsg
        :param routing_info: the routing info object for this dsg
        :param hostname: the machines hostname
        :param ip_tags: the collection of iptags generated by the tag allocator
        :param reverse_ip_tags: the collection of reverse iptags generated by\
                the tag allocator
        :param report_folder: the folder to write reports to
        :param write_text_specs: bool which says if test specs should be\
                written
        :param application_run_time_folder: the folder where application files\
                 are written
        """

    @abstractmethod
    def get_binary_file_name(self):
        """ Get the binary name for a given dataspecable vertex
        """

    @property
    def machine_time_step(self):
        """ The machine time step
        :return:
        """
        return self._machine_time_step

    @property
    def no_machine_time_steps(self):
        """ The number of machine time steps this model should run for
        :return:
        """
        return self._no_machine_time_steps

    def set_no_machine_time_steps(self, new_no_machine_time_steps):
        """ Set the number of machine time steps a model should run for

        :param new_no_machine_time_steps:
        :return:
        """
        if self._no_machine_time_steps is None:
            self._no_machine_time_steps = new_no_machine_time_steps
        else:
            raise exceptions.ConfigurationException(
                "cannot set the number of machine time steps of a given"
                " model once it has already been set")

    @staticmethod
    def get_data_spec_file_writers(
            processor_chip_x, processor_chip_y, processor_id, hostname,
            report_directory, write_text_specs,
            application_run_time_report_folder):
        """ Get data writers for the data specs

        :param processor_chip_x:
        :param processor_chip_y:
        :param processor_id:
        :param hostname:
        :param report_directory:
        :param write_text_specs:
        :param application_run_time_report_folder:
        :return:
        """
        binary_file_path = \
            AbstractPartitionedDataSpecableVertex.get_data_spec_file_path(
                processor_chip_x, processor_chip_y, processor_id, hostname,
                application_run_time_report_folder)
        data_writer = FileDataWriter(binary_file_path)

        # check if text reports are needed and if so initialise the report
        # writer to send down to dsg
        report_writer = None
        if write_text_specs:
            new_report_directory = os.path.join(report_directory,
                                                "data_spec_text_files")
            if not os.path.exists(new_report_directory):
                os.mkdir(new_report_directory)

            file_name = "{}_dataSpec_{}_{}_{}.txt"\
                        .format(hostname, processor_chip_x, processor_chip_y,
                                processor_id)
            report_file_path = os.path.join(new_report_directory, file_name)
            report_writer = FileDataWriter(report_file_path)

        return data_writer, report_writer

    @staticmethod
    def get_data_spec_file_path(
            processor_chip_x, processor_chip_y, processor_id, hostname,
            application_run_time_folder):
        """ Get the file path for the dsg writer

        :param processor_chip_x:
        :param processor_chip_y:
        :param processor_id:
        :param hostname:
        :param application_run_time_folder:
        :return:
        """

        if application_run_time_folder == "TEMP":
            application_run_time_folder = tempfile.gettempdir()

        binary_file_path = \
            application_run_time_folder + os.sep + "{}_dataSpec_{}_{}_{}.dat"\
            .format(hostname, processor_chip_x, processor_chip_y, processor_id)
        return binary_file_path

    @staticmethod
    def get_application_data_file_path(
            processor_chip_x, processor_chip_y, processor_id, hostname,
            application_run_time_folder):
        """ Get the file path for application data

        :param processor_chip_x:
        :param processor_chip_y:
        :param processor_id:
        :param hostname:
        :param application_run_time_folder:
        :return:
        """

        if application_run_time_folder == "TEMP":
            application_run_time_folder = tempfile.gettempdir()

        application_data_file_name = application_run_time_folder + os.sep + \
            "{}_appData_{}_{}_{}.dat".format(hostname, processor_chip_x,
                                             processor_chip_y, processor_id)
        return application_data_file_name

    def _write_basic_setup_info(self, spec, region_id):

        # Hash application title
        application_name = os.path.splitext(self.get_binary_file_name())[0]

        # Get first 32-bits of the md5 hash of the application name
        application_name_hash = hashlib.md5(application_name).hexdigest()[:8]

        # Write this to the system region (to be picked up by the simulation):
        spec.switch_write_focus(region=region_id)
        spec.write_value(data=int(application_name_hash, 16))
        spec.write_value(data=self._machine_time_step)
        # check for infinite runs and add data as required
        if self._no_machine_time_steps is None:
            spec.write_value(data=1)
            spec.write_value(data=0)
        else:
            spec.write_value(data=0)
            spec.write_value(data=self._no_machine_time_steps)

    @staticmethod
    def get_mem_write_base_address(processor_id):
        """ Get the base address of the processors registers

        :param processor_id:
        :return:
        """
        return 0xe5007000 + 128 * processor_id + 112

    @abstractmethod
    def is_partitioned_data_specable(self):
        """ Helper method for isinstance
        :return:
        """