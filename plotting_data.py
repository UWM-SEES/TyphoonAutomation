import pandas as pd
import pathlib as Path
import matplotlib.pyplot as plt

def plot_data(directory: Path):
    for x in directory.iterdir():
        if x.is_file():
            data_file = pd.read_csv(x)
            time = data_file["Time"]
            va = data_file["Battery inverter.Va"]
            vb = data_file["Battery inverter.Vb"]
            vc = data_file["Battery inverter.Vc"]
            ia = data_file["Battery inverter.I_a"]
            ib = data_file["Battery inverter.I_b"]
            ic = data_file["Battery inverter.I_c"]
            fig, (ax1, ax2) = plt.subplots(2, sharex=True)
            #Sets title for graphs
            ax1.set_title("Voltage")
            ax2.set_title("Current")
            if 'Data' in x.stem:
                fig.suptitle((x.stem).split('Data_',1)[1])

            else:
                fig.suptitle((x.stem).split('Capture_',1)[1])
                smaller_data_set = data_file.loc[data_file["Time"] < data_file["Time"].to_list()[0] + 3*(1/60)]
                time = smaller_data_set["Time"]
                va = smaller_data_set["Battery inverter.Va"]
                vb = smaller_data_set["Battery inverter.Vb"]
                vc = smaller_data_set["Battery inverter.Vc"]
                ia = smaller_data_set["Battery inverter.I_a"]
                ib = smaller_data_set["Battery inverter.I_b"]
                ic = smaller_data_set["Battery inverter.I_c"]

            # Plots data to graphs
            ax1.plot(time, va)
            ax1.plot(time, vb)
            ax1.plot(time, vc)
            ax2.plot(time, ia)
            ax2.plot(time, ib)
            ax2.plot(time, ic)
            plt.show()

path = Path.Path.cwd() / 'output' / 'data'
path1 = Path.Path.cwd() / 'output' / 'capture'
plot_data(path)
plot_data(path1)
print(1/60)