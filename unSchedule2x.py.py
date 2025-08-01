'''
        for resname, res in self.getDataManager().getResources().items():
            if ((res.getAutomated() is None) or (res.getAutomated()==False)) and not res.getType()=='Outsourced':
                for i in shiftlistman:
                    res.getSchedule()[i]=[]
                else:
                    for i in shiftlistaut:
                        res.getSchedule()[i]=[]
''' 