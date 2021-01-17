import AER_config as aer_config
import AER_theorist.darts.darts_config as darts_config
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from matplotlib.gridspec import GridSpec
from mpl_toolkits import mplot3d
import imageio
import time
import numpy as np
import os
import pandas


def plot_darts_summary(study_name, y_name, x1_name, x2_name=None, y_label=None, x1_label=None, x2_label=None, metric='min'):

    if y_label is None:
        y_label = y_name

    if x1_label is None:
        x1_label = x1_name

    if x2_label is None:
        x2_label = x2_name

    # determine directory for study results
    results_path = aer_config.studies_folder \
                        + study_name + "/" \
                        + aer_config.models_folder \
                        + aer_config.models_results_folder

    # read in all csv files
    files = list()
    for file in os.listdir(results_path):
        if file.endswith(".csv"):
            files.append(os.path.join(results_path, file))

    # generate a plot dictionary
    plot_dict = dict()
    plot_dict[darts_config.csv_arch_file_name] = list()
    plot_dict[y_name] = list()
    plot_dict[x1_name] = list()
    if x2_name is not None:
        plot_dict[x2_name] = list()

    # load csv files into a common dictionary
    for file in files:
        data = pandas.read_csv(file, header=0)
        plot_dict[darts_config.csv_arch_file_name].extend(data[darts_config.csv_arch_file_name])
        plot_dict[y_name].extend(data[y_name])
        plot_dict[x1_name].extend(data[x1_name])
        if x2_name is not None:
            plot_dict[x2_name].extend(data[x2_name])

    model_name_list = plot_dict[darts_config.csv_arch_file_name]
    x1_data = np.asarray(plot_dict[x1_name])
    y_data = np.asarray(plot_dict[y_name])
    if x2_name is None: # determine for each value of x1 the lowest y
        x1_data = np.asarray(plot_dict[x1_name])
        x1_unique = np.sort(np.unique(x1_data))

        y_plot = np.empty(x1_unique.shape)
        y_plot[:] = np.nan
        x1_plot = np.empty(x1_unique.shape)
        x1_plot[:] = np.nan
        for idx_unique, x1_unique_val in enumerate(x1_unique):
            y_match = list()
            model_name_match = list()
            for idx_data, x_data_val in enumerate(x1_data):
                if x1_unique_val == x_data_val:
                    y_match.append(y_data[idx_data])
                    model_name_match.append(model_name_list[idx_data])
            x1_plot[idx_unique] = x1_unique_val

            if metric is 'min':
                y_plot[idx_unique] = np.min(y_match)
                idx_target = np.argmin(y_match)
            elif metric is 'max':
                y_plot[idx_unique] = np.max(y_match)
                idx_target = np.argmax(y_match)
            elif metric is 'mean':
                y_plot[idx_unique] = np.mean(y_match)
                idx_target = 0
            else:
                raise Exception('Argument "metric" may either be "min", "max" or "mean".')

            print(x1_label + " = " + str(x1_unique_val) + " (" + str(y_plot[idx_unique]) + "): " + model_name_match[idx_target])

    else: # determine for each combination of x1 and x2 (unique rows) the lowest y
        x2_data = np.asarray(plot_dict[x2_name])
        x2_unique = np.sort(np.unique(x2_data))

        y_plot = list()
        x1_plot = list()
        x2_plot = list()
        for idx_x2_unique, x2_unique_val in enumerate(x2_unique):

            # collect all x1 and y values matching the current x2 value
            model_name_x2_match = list()
            y_x2_match=list()
            x1_x2_match = list()
            for idx_x2_data, x2_data_val in enumerate(x2_data):
                if x2_unique_val == x2_data_val:
                    model_name_x2_match.append(model_name_list[idx_x2_data])
                    y_x2_match.append(y_data[idx_x2_data])
                    x1_x2_match.append(x1_data[idx_x2_data])

            # now determine unique x1 values for current x2 value
            x1_unique = np.sort(np.unique(x1_x2_match))
            x1_x2_plot = np.empty(x1_unique.shape)
            x1_x2_plot[:] = np.nan
            y_x2_plot = np.empty(x1_unique.shape)
            y_x2_plot[:] = np.nan
            for idx_x1_unique, x1_unique_val in enumerate(x1_unique):
                y_x2_x1_match = list()
                model_name_x2_x1_match = list()
                for idx_x1_data, x1_data_val in enumerate(x1_x2_match):
                    if x1_unique_val == x1_data_val:
                        model_name_x2_x1_match.append(model_name_x2_match[idx_x1_data])
                        y_x2_x1_match.append(y_x2_match[idx_x1_data])
                x1_x2_plot[idx_x1_unique] = x1_unique_val

                if metric is 'min':
                    y_x2_plot[idx_x1_unique] = np.min(y_x2_x1_match)
                    idx_target = np.argmin(y_x2_x1_match)
                elif metric is 'max':
                    y_x2_plot[idx_x1_unique] = np.max(y_x2_x1_match)
                    idx_target = np.argmax(y_x2_x1_match)
                elif metric is 'mean':
                    y_x2_plot[idx_x1_unique] = np.mean(y_x2_x1_match)
                    idx_target = 0
                else:
                    raise Exception('Argument "metric" may either be "min", "max" or "mean".')

                print(x1_label + " = " + str(x1_unique_val) + ", " + \
                      x2_label + " = " + str(x2_unique_val) + " (" + \
                    str(y_x2_plot[idx_x1_unique]) + "): " + model_name_x2_x1_match[idx_target])
            y_plot.append(y_x2_plot)
            x1_plot.append(x1_x2_plot)
            x2_plot.append(x2_unique_val)
    # plot

    # todo: incorporate
    # sns.despine(trim=True)
    # plt.axhline(1, c = 'b')

    if x2_name is None:

        data_plot = pandas.DataFrame({x1_label:x1_plot, y_label:y_plot})
        sns.lineplot(x=x1_label, y=y_label, data=data_plot)
        sns.despine(trim=True)
        plt.show()

    else:

        # produce data frame:
        x1_df = list()
        x2_df = list()
        y_df = list()
        for idx_x2, x2 in enumerate(x2_plot):
            for idx_x1, x1 in enumerate(x1_plot[idx_x2]):
                x1_df.append(x1)
                x2_df.append(x2)
                y_df.append(y_plot[idx_x2][idx_x1])

        data_plot = pandas.DataFrame({x1_label: x1_df, x2_label: x2_df, y_label: y_df})
        sns.lineplot(data=data_plot, x=x1_label, y=y_label, hue=x2_label, linewidth = 1)
        sns.despine(trim=True)
        plt.show()

# old
class DebugWindow:

    def __init__(self, num_epochs, numArchEdges=1, numArchOps=1, ArchOpsLabels=(), fitPlot3D = False, show_arch_weights=True):

        # initialization
        matplotlib.use("TkAgg") # need to add this for PyCharm environment

        plt.ion()

        # SETTINGS
        self.show_arch_weights = show_arch_weights
        self.fontSize = 10

        self.performancePlot_limit = (0, 1)
        self.modelFitPlot_limit = (0, 500)
        self.mismatchPlot_limit = (0, 1)
        self.architectureWeightsPlot_limit = (0.1, 0.2)

        self.numPatternsShown = 100

        # FIGURE
        self.fig = plt.figure()
        self.fig.set_size_inches(13, 7)

        if self.show_arch_weights is False:
            numArchEdges = 0

        # set up grid
        numRows = np.max((1+np.ceil((numArchEdges+1)/4), 2))
        gs = GridSpec(numRows.astype(int), 4, figure=self.fig)

        self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.9, wspace=0.4, hspace=0.5)
        self.modelGraph = self.fig.add_subplot(gs[1, 0])
        self.performancePlot = self.fig.add_subplot(gs[0, 0])
        self.modelFitPlot = self.fig.add_subplot(gs[0, 1])
        if fitPlot3D:
            self.mismatchPlot = self.fig.add_subplot(gs[0, 2], projection='3d')
        else:
            self.mismatchPlot = self.fig.add_subplot(gs[0, 2])
        self.examplePatternsPlot = self.fig.add_subplot(gs[0, 3])

        self.architecturePlot = []

        for edge in range(numArchEdges):
            row = np.ceil((edge+2)/4).astype(int)
            col = ((edge+1) % 4)
            self.architecturePlot.append(self.fig.add_subplot(gs[row, col]))

        self.colors = ('black', 'red', 'green', 'blue', 'purple', 'orange', 'brown', 'pink', 'grey', 'olive', 'cyan', 'yellow', 'skyblue', 'coral', 'magenta', 'seagreen', 'sandybrown')

        # PERFORMANCE PLOT
        x = 1
        y = 1
        self.train_error, = self.performancePlot.plot(x, y, 'r-')
        self.valid_error, = self.performancePlot.plot(x, y, 'b', linestyle='dashed')

        # set labels
        self.performancePlot.set_xlabel('Epoch', fontsize = self.fontSize)
        self.performancePlot.set_ylabel('Cross-Entropy Loss', fontsize = self.fontSize)
        self.performancePlot.set_title('Performance', fontsize = self.fontSize)
        self.performancePlot.legend((self.train_error, self.valid_error), ('training error', 'validation error'))

        # adjust axes
        self.performancePlot.set_xlim(0, num_epochs)
        self.performancePlot.set_ylim(self.performancePlot_limit[0], self.performancePlot_limit[1])

        # MODEL FIT PLOT
        x = 1
        y = 1
        self.BIC, = self.modelFitPlot.plot(x, y, color='black')
        self.AIC, = self.modelFitPlot.plot(x, y, color='grey')

        # set labels
        self.modelFitPlot.set_xlabel('Epoch', fontsize = self.fontSize)
        self.modelFitPlot.set_ylabel('Information Criterion', fontsize = self.fontSize)
        self.modelFitPlot.set_title('Model Fit', fontsize = self.fontSize)
        self.modelFitPlot.legend((self.BIC, self.AIC), ('BIC', 'AIC'))

        # adjust axes
        self.modelFitPlot.set_xlim(0, num_epochs)
        self.modelFitPlot.set_ylim(self.modelFitPlot_limit[0], self.modelFitPlot_limit[1])

        # RANGE PREDICTION FIT PLOT
        x = 1
        y = 1
        if fitPlot3D:
            x = np.arange(0, 1, 0.1)
            y = np.arange(0, 1, 0.1)
            X, Y = np.meshgrid(x, y)
            Z = X * np.exp(-X - Y)

            self.range_target = self.mismatchPlot.plot_surface(X, Y, Z)
            self.range_prediction = self.mismatchPlot.plot_surface(X, Y, Z)
            self.mismatchPlot.set_zlim(self.mismatchPlot_limit[0], self.mismatchPlot_limit[1])

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus 1', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Stimulus 2', fontsize=self.fontSize)
            self.mismatchPlot.set_zlabel('Outcome Value', fontsize=self.fontSize)

        else:
            self.range_target, = self.mismatchPlot.plot(x, y, color='black')
            self.range_prediction, = self.mismatchPlot.plot(x, y, '--', color='red')

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus Value', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Outcome Value', fontsize=self.fontSize)
            self.mismatchPlot.legend((self.range_target, self.range_prediction), ('target', 'prediction'))

        self.mismatchPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)

        # adjust axes
        self.mismatchPlot.set_xlim(0, 1)
        self.mismatchPlot.set_ylim(0, 1)

        # ARCHITECTURE WEIGHT PLOT
        if self.show_arch_weights:

            self.architectureWeights = []
            for idx, architecturePlot in enumerate(self.architecturePlot):
                plotWeights = []
                x = 1
                y = 1
                for op in range(numArchOps):
                    plotWeight, = architecturePlot.plot(x, y, color=self.colors[op])
                    plotWeights.append(plotWeight)

                # set legend
                if(idx == 0):
                    architecturePlot.legend(plotWeights, ArchOpsLabels, prop={'size': 6})

                # add labels
                architecturePlot.set_ylabel('Weight', fontsize = self.fontSize)
                architecturePlot.set_title('(' + str(idx) + ') Edge Weight', fontsize = self.fontSize)
                if(idx == len(self.architecturePlot) - 1):
                    architecturePlot.set_xlabel('Epoch', fontsize = self.fontSize)

                # adjust axes
                architecturePlot.set_xlim(0, num_epochs)
                architecturePlot.set_ylim(self.architectureWeightsPlot_limit[0], self.architectureWeightsPlot_limit[1])

                self.architectureWeights.append(plotWeights)


        # draw
        plt.draw()


    def update(self, train_error=None, valid_error=None, weights=None, BIC=None, AIC=None, model_graph=None, range_input1=None, range_input2=None, range_target=None, range_prediction=None, target=None, prediction=None):

        # update training error
        if train_error is not None:
            self.train_error.set_xdata(np.linspace(1, len(train_error), len(train_error)))
            self.train_error.set_ydata(train_error)

        # update validation error
        if valid_error is not None:
            self.valid_error.set_xdata(np.linspace(1, len(valid_error), len(valid_error)))
            self.valid_error.set_ydata(valid_error)

        # update BIC
        if BIC is not None:
            self.BIC.set_xdata(np.linspace(1, len(BIC), len(BIC)))
            self.BIC.set_ydata(BIC)

        # update AIC
        if AIC is not None:
            self.AIC.set_xdata(np.linspace(1, len(AIC), len(AIC)))
            self.AIC.set_ydata(AIC)

        # update target vs. prediction plot
        if range_input1 is not None and range_target is not None and range_prediction is not None and range_input2 is None:
            self.range_target.set_xdata(range_input1)
            self.range_target.set_ydata(range_target)
            self.range_prediction.set_xdata(range_input1)
            self.range_prediction.set_ydata(range_prediction)
        elif range_input1 is not None and range_target is not None and range_prediction is not None and range_input2 is not None:

            # update plot
            self.mismatchPlot.cla()
            self.range_target = self.mismatchPlot.plot_surface(range_input1, range_input2, range_target, color = (0, 0, 0, 0.5))
            self.range_prediction = self.mismatchPlot.plot_surface(range_input1, range_input2, range_prediction, color = (1, 0, 0, 0.5))

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus 1', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Stimulus 2', fontsize=self.fontSize)
            self.mismatchPlot.set_zlabel('Outcome Value', fontsize=self.fontSize)
            self.mismatchPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)



        # update example pattern plot
        if target is not None and prediction is not None:

            # select limited number of patterns
            self.numPatternsShown = np.min((self.numPatternsShown, target.shape[0]))
            target = target[0:self.numPatternsShown, :]
            prediction = prediction[0:self.numPatternsShown, :]

            im = np.concatenate((target, prediction), axis=1)
            self.examplePatternsPlot.cla()
            self.examplePatternsPlot.imshow(im, interpolation='nearest', aspect='auto')
            x = np.ones(target.shape[0]) * (target.shape[1]-0.5)
            y = np.linspace(1, target.shape[0], target.shape[0])
            self.examplePatternsPlot.plot(x, y, color='red')

            # set labels
            self.examplePatternsPlot.set_xlabel('Output', fontsize=self.fontSize)
            self.examplePatternsPlot.set_ylabel('Pattern', fontsize=self.fontSize)
            self.examplePatternsPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)

        if self.show_arch_weights:
            # update weights
            if weights is not None:
                for plotIdx, architectureWeights in enumerate(self.architectureWeights):
                    for lineIdx, plotWeight in enumerate(architectureWeights):
                        plotWeight.set_xdata(np.linspace(1, weights.shape[0], weights.shape[0]))
                        plotWeight.set_ydata(weights[:, plotIdx, lineIdx])

        # draw current graph
        if model_graph is not None:
            im = imageio.imread(model_graph)
            self.modelGraph.cla()
            self.modelGraph.imshow(im)
            self.modelGraph.axis('off')

        # re-draw plot
        plt.draw()
        plt.pause(0.02)

