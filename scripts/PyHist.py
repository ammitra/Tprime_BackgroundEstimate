import numpy as np
class PyHist:
    def __init__(self, histo):
        """
        Initializes the class PyHist object.
        Parameters:
        - histo (TH1): The input ROOT histogram
        """
        self.histo_name = histo.GetName()
        self.bin_values = np.array([histo.GetBinContent(i) for i in range(1, histo.GetNbinsX() + 1)])
        self.bin_error_low = np.array([histo.GetBinErrorLow(i) for i in range(1, histo.GetNbinsX() + 1)])
        self.bin_error_hi = np.array([histo.GetBinErrorUp(i) for i in range(1, histo.GetNbinsX() + 1)])
        self.bin_edges = np.array([histo.GetBinLowEdge(i) for i in range(1, histo.GetNbinsX() + 2)])
        self.bin_widths = np.array([histo.GetBinWidth(i) for i in range(1, histo.GetNbinsX() + 1)])
        self.bin_error = np.array([histo.GetBinError(i) for i in range(1, histo.GetNbinsX() + 1)])
        self.is_normalized_by_width = False

    def divide_by_bin_width(self):
        """
        Divides the bin values and errors by the bin widths.
        """
        if not self.is_normalized_by_width:
            self.bin_values = np.array([val / width for val, width in zip(self.bin_values, self.bin_widths)])
            self.bin_error_low = np.array([err / width for err, width in zip(self.bin_error_low, self.bin_widths)])
            self.bin_error_hi = np.array([err / width for err, width in zip(self.bin_error_hi, self.bin_widths)])
            self.bin_error = np.array([err / width for err, width in zip(self.bin_error, self.bin_widths)])
            self.is_normalized_by_width = True
        else:
            print("Already normalized by bin width.")

    def get_error_pairs(self):
        """
        For use with pyplot.errorbar.
        """
        return np.array([self.bin_error_low, self.bin_error_hi])
    
    def get_bin_centers(self):
        """
        Calculates the bin centers for the histogram.
        Returns:
        - List of bin centers.
        """
        return np.array([(self.bin_edges[i] + self.bin_edges[i + 1]) / 2 for i in range(len(self.bin_edges) - 1)])