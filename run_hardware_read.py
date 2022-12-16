import xarray as xr
import numpy as np
import niswitch

from pySwitch import Functions as matrix
from KtM960x_python_API import M9615A_Session
from KtM960x_python_API import M9615A_Enums

from MTJ_XBAR.Keysight_SMU_Functions import all_switchmatrix_connections_to_grnd
from generic_save_and_load import save_xrDataArray

from MTJ_XBAR import probecard

probecard_rows = probecard.row15x15[1:]
probecard_cols = probecard.col15x15[1:]

# SMU 5 Channel #'s are 1-5
# Switchmatrix 4 Channel #'s are 0-3
# SMU Channels 1-4 are hardwired to Switchmatrix Channels 0-3
# If SMU channel 4 is designated as grnd, this must correspond to switchmatrix channel 3
smu_channel_apply = 1
smu_channel_lo = 3
smu_channel_grnd = 4

measurement_current_limit = 10e-3
measurement_aperture = 1e-3

voltage_trigger_timer = 10e-3
measurement_trigger_timer = 10e-3
measurement_trigger_delay = 3e-3

v_read = 0.2

switchblock0 = "PXI1Slot5"
switchblock1 = "PXI1Slot4"
switchblock2 = "PXI1Slot3"
switchmatrix = [
    niswitch.Session(resource_name=switchblock0, simulate=False, reset_device=False),
    niswitch.Session(resource_name=switchblock1, simulate=False, reset_device=False),
    niswitch.Session(resource_name=switchblock2, simulate=False, reset_device=False),
]
print("switchmatrix session created")

try:
    # instantiate session
    # 1st True - query instrument model and make sure driver supported
    # 2nd True - Reset instrument to default values - good to do generally in case settings configured badly last time
    session = M9615A_Session("PXI213::0::INSTR", True, True, "")

    # make sure when the instrument is in non-running state the SMU's channels are connected and apply 0 V
    # when instrument is reset, default is break SMU connections while applying 0 V
    # want to have SMU's connected to minimize time devices are floating
    for i in range(1, 6):
        identifier = "Output{}".format(i)
        session.RepCap(identifier).OUTPUT_OFF_CONDITION = M9615A_Enums.OFF_CONDITION_ZERO

    # make sure instrument is in non-running state by aborting all channels
    session.Funcs.Abort(5, [1, 2, 3, 4, 5])
    print("M9615A session created")

    # disconnect all switchmatrix column connections from all channels and only reconnect all column connections channel designated as ground
    all_switchmatrix_connections_to_grnd(switchmatrix, smu_channel_grnd - 1)

    # configure SMU settings
    # Output - configures the output mode (voltage/current) and settings for that channel
    # Transient - configures applied voltage sequence and timing settings for that channel
    # Measurement - configures measurement and timing settings for that channel
    identifier = "Transient{}".format(smu_channel_apply)
    session.RepCap(identifier).TRANSIENT_VOLTAGE_MODE = M9615A_Enums.OUTPUT_MODE_LIST
    session.RepCap(identifier).TRANSIENT_TRIGGER_SOURCE = M9615A_Enums.MEASUREMENT_TRIGGER_SOURCE_TIMER
    session.RepCap(identifier).TRANSIENT_TRIGGER_TIMER = voltage_trigger_timer

    identifier = "Transient{}".format(smu_channel_lo)
    session.RepCap(identifier).TRANSIENT_VOLTAGE_MODE = M9615A_Enums.OUTPUT_MODE_LIST
    session.RepCap(identifier).TRANSIENT_TRIGGER_SOURCE = M9615A_Enums.MEASUREMENT_TRIGGER_SOURCE_TIMER
    session.RepCap(identifier).TRANSIENT_TRIGGER_TIMER = voltage_trigger_timer

    identifier = "Measurement{}".format(smu_channel_apply)
    session.RepCap(identifier).MEASUREMENT_CURRENT_APERTURE = measurement_aperture
    session.RepCap(identifier).MEASUREMENT_VOLTAGE_APERTURE = measurement_aperture
    session.RepCap(identifier).MEASUREMENT_TRIGGER_DELAY = measurement_trigger_delay
    session.RepCap(identifier).MEASUREMENT_TRIGGER_SOURCE = M9615A_Enums.MEASUREMENT_TRIGGER_SOURCE_TIMER
    session.RepCap(identifier).MEASUREMENT_TRIGGER_TIMER = measurement_trigger_timer
    session.RepCap(identifier).MEASUREMENT_CURRENT_LIMIT = measurement_current_limit
    # session.RepCap(identifier).MEASUREMENT_CURRENT_SEAMLESS_RANGING_ENABLED = True

    identifier = "Measurement{}".format(smu_channel_lo)
    session.RepCap(identifier).MEASUREMENT_CURRENT_APERTURE = measurement_aperture
    session.RepCap(identifier).MEASUREMENT_VOLTAGE_APERTURE = measurement_aperture
    session.RepCap(identifier).MEASUREMENT_TRIGGER_DELAY = measurement_trigger_delay
    session.RepCap(identifier).MEASUREMENT_TRIGGER_SOURCE = M9615A_Enums.MEASUREMENT_TRIGGER_SOURCE_TIMER
    session.RepCap(identifier).MEASUREMENT_TRIGGER_TIMER = measurement_trigger_timer
    session.RepCap(identifier).MEASUREMENT_CURRENT_LIMIT = measurement_current_limit
    # session.RepCap(identifier).MEASUREMENT_CURRENT_SEAMLESS_RANGING_ENABLED = True

    voltages_apply = [v_read]
    voltages_lo = [0]

    # set the sequence of voltages and measurements for SMU apply and lo channels
    identifier = "Transient{}".format(smu_channel_apply)
    session.RepCap(identifier).TRANSIENT_TRIGGER_COUNT = len(voltages_apply)
    session.Funcs.TransientVoltageConfigureList(identifier, len(voltages_apply), voltages_apply)

    identifier = "Measurement{}".format(smu_channel_apply)
    session.RepCap(identifier).MEASUREMENT_TRIGGER_COUNT = len(voltages_apply)

    identifier = "Transient{}".format(smu_channel_lo)
    session.RepCap(identifier).TRANSIENT_TRIGGER_COUNT = len(voltages_lo)
    session.Funcs.TransientVoltageConfigureList(identifier, len(voltages_lo), voltages_lo)

    identifier = "Measurement{}".format(smu_channel_lo)
    session.RepCap(identifier).MEASUREMENT_TRIGGER_COUNT = len(voltages_lo)

    # create a list of channels to initiate and pull data from - this is needed in the Keysight functions
    channel_list = [smu_channel_apply, smu_channel_lo]

    # create an uninitialized numpy array data structure to store the data - make sure to create the correct dimensions
    # uninitialized means it will have random data values - used because it's faster than initializing all data to 0's
    # dimension 1 - rows
    # dimension 2 - columns
    # dimension 3 - number of separate measured quantities
    # dimension 4 - number of values measured (ex. 50 sweep points)
    array_data = np.empty((len(probecard_rows), len(probecard_cols), 6, 1))

    # iterate over all devices by connecting a column and iterating over all rows before connecting next column
    # rows and columns sub-indexed to [1:]
    # switchmatrix channel indices -1 due to smu channel offset
    for q in range(len(probecard_cols)):
        # connect col to channel_lo
        matrix.connectloadtosource([probecard_cols[q]], [smu_channel_lo - 1], switchmatrix)
        # disconnect col from channel_ground
        matrix.disconnectloadtosource([probecard_cols[q]], [smu_channel_grnd - 1], switchmatrix)

        for p in range(len(probecard_rows)):
            # connect row to channel_apply
            matrix.connectloadtosource([probecard_rows[p]], [smu_channel_apply - 1], switchmatrix)
            # disconnect row from channel_ground
            matrix.disconnectloadtosource([probecard_rows[p]], [smu_channel_grnd - 1], switchmatrix)

            # initiate the test by calling initiate on the channels
            session.Funcs.Initiate(len(channel_list), channel_list)
            print("Initiated")
            # wait for the test to complete
            completed = session.Funcs.SystemWaitForOperationComplete(5000)
            print("Completed!")

            # check if completed was true to see if the measurement completed successfully
            # fetch the data
            if completed:
                channels, smu_apply_v, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_VOLTAGE, 1, [smu_channel_apply], len(voltages_apply), []
                )
                # print(np.array(smu_apply_v))
                channels, smu_apply_i, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_CURRENT, 1, [smu_channel_apply], len(voltages_apply), []
                )
                # print(np.array(smu_apply_i))
                channels, smu_apply_t, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_TIME, 1, [smu_channel_apply], len(voltages_apply), []
                )
                # print(np.array(smu_apply_t))
                channels, smu_lo_v, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_VOLTAGE, 1, [smu_channel_lo], len(voltages_lo), []
                )
                # print(np.array(smu_lo_v))
                channels, smu_lo_i, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_CURRENT, 1, [smu_channel_lo], len(voltages_lo), []
                )
                # print(np.array(smu_lo_i))
                channels, smu_lo_t, actual = session.Funcs.MeasurementFetchArrayData(
                    M9615A_Enums.MEASUREMENT_FETCH_TYPE_TIME, 1, [smu_channel_lo], len(voltages_lo), []
                )
                # print(np.array(smu_lo_t))

            # save the data for each device in a multi-dimensional numpy array
            array_data[p, q, 0, 0] = smu_apply_v[0]
            array_data[p, q, 1, 0] = smu_lo_v[0]
            array_data[p, q, 2, 0] = smu_apply_i[0]
            array_data[p, q, 3, 0] = smu_lo_i[0]
            array_data[p, q, 4, 0] = smu_apply_t[0]
            array_data[p, q, 5, 0] = smu_lo_t[0]

            # connect row to channel_ground
            matrix.connectloadtosource([probecard_rows[p]], [smu_channel_grnd - 1], switchmatrix)
            # disconnect row from channel_apply
            matrix.disconnectloadtosource([probecard_rows[p]], [smu_channel_apply - 1], switchmatrix)

        # connect col to channel_ground
        matrix.connectloadtosource([probecard_cols[q]], [smu_channel_grnd - 1], switchmatrix)
        # disconnect col from channel_lo
        matrix.disconnectloadtosource([probecard_cols[q]], [smu_channel_lo - 1], switchmatrix)

    # Make the previously created numpy array with the data into an xrDataArray and name the dimensions and coordinates accordingly
    array_data = xr.DataArray(
        np.asarray(array_data),
        dims=("row", "col", "measured_quantity", "vals"),
        coords={
            "measured_quantity": [
                "pulse1_read_apply_voltage",
                "pulse1_read_lo_voltage",
                "pulse1_read_apply_current",
                "pulse1_read_lo_current",
                "pulse1_read_apply_time",
                "pulse1_read_lo_time",
            ]
        },
    )

    # save the xrDataArray with metadata from this test
    save_xrDataArray(
        array_data,
        attrs=dict(
            v_read=v_read,
            measurement_aperture=measurement_aperture,
            measurement_current_limit=measurement_current_limit,
            voltage_trigger_timer=voltage_trigger_timer,
            measurement_trigger_timer=measurement_trigger_timer,
            measurement_trigger_delay=measurement_trigger_delay,
        ),
    )

# Make sure to close the instrument session if the test fails at a certain point
except Exception as e:
    print("exception occurred")
    print(e)
    session.Funcs.Abort(5, [1, 2, 3, 4, 5])
    session.Funcs.close()
    switchmatrix[0].close()
    switchmatrix[1].close()
    switchmatrix[2].close()

else:
    print("Great Success!")
    session.Funcs.Abort(5, [1, 2, 3, 4, 5])
    session.Funcs.close()
    switchmatrix[0].close()
    switchmatrix[1].close()
    switchmatrix[2].close()
