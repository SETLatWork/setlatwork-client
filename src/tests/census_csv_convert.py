'''
Created on 5/05/2014

@author: burkej
'''
import csv
from collections import OrderedDict

if __name__ == '__main__':
    folder = r'C:\Users\burkej\Documents\Projects\Census Lookup Tables\Data\\'
    files = ['2013-mb-dataset-Total-New-Zealand-Dwelling', '2013-mb-dataset-Total-New-Zealand-Family', '2013-mb-dataset-Total-New-Zealand-Household', '2013-mb-dataset-Total-New-Zealand-Individual-Part-1', '2013-mb-dataset-Total-New-Zealand-Individual-Part-2', '2013-mb-dataset-Total-New-Zealand-Individual-Part-3a', '2013-mb-dataset-Total-New-Zealand-Individual-Part-3b']
    
    replace_dict = OrderedDict([('Building', 'Bldg'),('Government','Govt'),('Private','Pvt'),('State-Owned Enterprise','SOE'),('Industry','Ind'),('Division','Div'),('Resident','Res'),('Population','Pop'),('Professional','Prof'),('Occupation','Occ'),('Dwelling','Dwlg'),('Year','Yr'),('Operations','Ops'),('Address','Addr'),('Count','Cnt'),('Major','Maj'),('Group','Grp'),('Registered','Regd')])
    largest_col = ''
    # loop through the list of files to format
    for filename in files:
        
        # get the first line from the csv file, which will contains the headers
        headers = None
        with open(folder + filename + '.csv', 'rb') as f:
            my_reader = csv.reader(f)
            headers = my_reader.next()
        
        # loop through the headers and reformat them to:
        # title case, no spaces, no brackets, no fwd slash, no word Census
        i = 0
        for col in headers:
            temp1 = col.replace('_', ' ').title()
            for k, v in replace_dict.iteritems():
                temp1 = temp1.replace(k, v)
            for x in range(23):
                temp1 = temp1.replace("(%s)" %x, '')
            temp2 = temp1.replace(' ','').replace('/','').replace('Census','')
            headers[i] = temp2
            if len(temp2) > len(largest_col):
                largest_col = temp2
            i += 1
        
        for col in headers:
            print col
        
        # write the changes to a new csv file with _formatted suffix   
        with open(folder + filename + '_formatted.csv', 'wb') as f:
            w = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            # write the headers first
            w.writerow(headers)
            
            # open the csv file to read the remaining rows
            with open(folder + filename + '.csv', 'rb') as f:
                my_reader = csv.reader(f)
                # skip the first row, it contains the headers
                headers = my_reader.next()
                # loop through the remaining rows
                for row in my_reader:
                    # replace any cells with ..C in them with 0
                    temp = [x if not x == '..C' else 0 for x in row]
                    # replace any cells with * in them with 0
                    temp = [x if not x == '*' else 0 for x in temp]
                    
                    temp = [x if not x == '..' else 0 for x in temp]
                    # write to csv
                    w.writerow(temp)
    
    print 'Largest Column Name: %s' % largest_col