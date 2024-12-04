'''
Script to parse a Combine data card and remove systematics from certain regions for certain processes.
'''
from collections import OrderedDict 

def parse_card(card):
    f = open(card,'r')
    lines = [i.strip() for i in f.readlines()]
    newlines = lines.copy()
    # 2DAlphabet uses 120-character-long strings of "-" to delineate regions of the card.
    # We want to gather the indices of all of these so we know which lines to parse
    d_idxs = [i for i, x in enumerate(lines) if x == '-'*120]
    # The bin and processes information will be on the two lines following the 3rd delineation
    # NOTE: these two lines will have a whitespace where "shapes" belongs for the nuisance parameter lines. Therefore there will be a one-index offset b/w this line and the nuisance parameter lines. 
    bins  = lines[d_idxs[2]+1]
    procs = lines[d_idxs[2]+2]
    # Now we want the indices of all mcstats parameter lines
    np_idxs = [i for i, x in enumerate(lines) if 'mcstats' in x]
    d = OrderedDict([(i,{'old':lines[i],'new':''}) for i in np_idxs])    
    # Let's associate the bin and procs
    bin_proc = [[bins.split()[i],procs.split()[i]] for i in range(len(bins.split()))]
    for np_idx in np_idxs:  # loop over the mcstats nuisance lines
        # get the original line describing this nuisance 
        old = lines[np_idx]
        old_split = old.split()
        new_split = old_split.copy()
        for i, bp in enumerate(bin_proc): # loop over the associated bin and procs
            if i == 0: continue # this will just be ['bin','process']
            # we are looking for ttbar processes 
            if 'ttbar_' in bp[1]:
                # check if the bin is 'ttbarCR_pass_LOW/SIG/HIGH'
                if 'ttbarCR_pass' in bp[0]:
                    continue
                else:
                    # get the old value, check that it is 1.0
                    old_val = old_split[i+1]
                    assert(old_val == '1.0')
                    new_val = '-'
                    # replace the old value for the new syst line
                    new_split[i+1] = new_val

        # get number of 1.0 in the new list - should be 12
        number_new = [i for i in new_split if i == '1.0']
        assert(len(number_new) == 12)
        # After doing this, create the new line string        
        new_line = ''
        for syst_effect in new_split:
            new_line += '{0:20} '.format(syst_effect)
        # now replace this line in the new_lines list 
        newlines[np_idx] = new_line 
        d[np_idx]['new'] = new_line # just for comparison 

    # Now write it all out to a file 
    with open('card_new.txt','w') as fnew:
        for line in newlines:
            fnew.write(f'{line}\n')

    # write it to a debug file as well
    with open('DEBUG.txt','w') as fdebug:
        fdebug.write(f'{"-"*120}\n')
        fdebug.write(f'{bins}\n')
        fdebug.write(f'{procs}\n')
        fdebug.write(f'{"-"*120}\n')
        for k, v in d.items():
            fdebug.write('\n')
            fdebug.write(f'{v["old"]}\n')
            fdebug.write(f'{v["new"]}\n')





parse_card('card_original.txt')
