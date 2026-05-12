from datetime import timedelta,date
import random
import pandas as pd


#______________________________________________________________________________________________________
class RandomVar(object):
    def __init__(self):
        self.Sampling = []
        self.Parameters = dict()

    def getParameters(self):
        return self.Parameters

    def getSampling(self):
        return self.Sampling

    def sampleValue(self):
        # will be overwritten by specific subobject
        return random.choice(self.getSampling())


class LogNormalVar(RandomVar):
    def __init__(self):
        super().__init__()

        N = len(self.getSampling())

        mean = np.log(max(1, N / 2))
        sigma = 0.4

        self.Parameters["mean"] = mean
        self.Parameters["sigma"] = sigma


    def sampleValue(self):
        index = int(np.random.lognormal(
            self.Parameters["mean"],
            self.Parameters["sigma"]
        ))

        # clamp to valid range
        index = max(0, min(index, len(self.Sampling) - 1))
        return self.Sampling[index]
        

class NormalVar(RandomVar):
    def __init__(self):
        super().__init__()

        N = len(self.getSampling())

        # automatic mean and std
        mean_index = (N - 1) / 2
        std_index = N / 6

        self.Parameters["mean_index"] = mean_index
        self.Parameters["std_index"] = std_index


    def sampleValue(self):
        index = int(np.random.normal(
            self.Parameters["mean_index"],
            self.Parameters["std_index"]
        ))

        index = max(0, min(index, len(self.Sampling) - 1))
        return self.Sampling[index]
#____________________________________________________________________________________

    
