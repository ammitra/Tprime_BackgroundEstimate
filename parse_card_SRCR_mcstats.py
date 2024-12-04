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
    # Since we have different mcstats for SR and CR, we need to make a dict to store which are which
    np_idxs = {}
    for i, x in enumerate(lines):
        if 'mcstats' in x:
            np_idxs[i] = x
        elif 'DAK8Top_tag' in x: # because DAK8 top-tagging is specific to ttbarCR, we have to remove it from SR (2DAlphabet applies it to all regions)
            np_idxs[i] = x
        elif 'PNetXbb_mistag' in x: # again, this is only applicable to SR, but gets added to CR as well by 2DAlphabet
            np_idxs[i] = x
    d = OrderedDict([(i,{'old':lines[i],'new':''}) for i in np_idxs.keys()])
    # Let's associate the bin and procs
    bin_proc = [[bins.split()[i],procs.split()[i]] for i in range(len(bins.split()))]
    for np_idx, np_name in np_idxs.items():  # loop over the mcstats nuisance lines
        # get the original line describing this nuisance 
        old = lines[np_idx]
        print('DEBUG-------------------------------------------------------------------------------------------')
        print(old)
        old_split = old.split()
        new_split = old_split.copy()
        print(new_split)
        print('DEBUG-------------------------------------------------------------------------------------------')
        for i, bp in enumerate(bin_proc): # loop over the associated bin and procs
            print(i,bp)
            if i == 0: continue # this will just be ['bin','process']

            # For some reason the ZJets_18 proc in SR_Fail_LOW is missing a '-' entry for these...

            if 'Background' in bp[1]: continue # this is just qcd stuff, ignore it 

            # MCSTATS 
            if 'mcstats' in np_name:
                # we are looking for ttbar processes 
                if 'ttbar_' in bp[1]:
                    # need to make sure SR-specific mcstats params don't get assigned to ttbarCR, and vice-versa
                    # There will be 48 "1.0" values. The first 24 belong to ttbarCR_fail/pass_LOW/SIG/HIGH for ttbar in the 4 years (24 total)
                    #                                The next 24 belong to SR_fail/pass_LOW/SIG/HIGH for ttbar in the 4 years (another 24)
                    if ('SR_pass' in bp[0]):
                        old_val = old_split[i+1]
                        assert(old_val == '1.0')
                        # this bin/proc combo should keep the systematic iff the nuisance param name has 'SR_pass' in it
                        if 'SR_pass' in new_split[0]: # the first index is the syst name 
                            # Do nothing 
                            pass
                        else:
                            new_split[i+1] = '-'
                    elif ('CR_pass' in bp[0]):
                        old_val = old_split[i+1]
                        assert(old_val == '1.0')
                        if 'CR_pass' in new_split[0]:
                            pass
                        else:
                            new_split[i+1] = '-'

                    else:
                        # get the old value, check that it is 1.0
                        old_val = old_split[i+1]
                        assert(old_val == '1.0')
                        new_val = '-'
                        # replace the old value for the new syst line
                        new_split[i+1] = new_val

            # Remove DAK8 tagging from SR (applied only to ttbar)
            elif 'DAK8' in np_name:
                if ('SR' in bp[0]) and ('ttbar_' in bp[1]):
                    old_val = old_split[i+1]
                    assert(old_val == '1.0')
                    new_split[i+1] = '-'
            # Remove PNetXbb mistag from CR (applied only to ttbar)
            elif 'Xbb' in np_name:
                if ('CR' in bp[0]) and ('ttbar_' in bp[1]):
                    old_val = old_split[i+1]
                    assert(old_val == '1.0')
                    new_split[i+1] = '-'


        # get number of 1.0 in the new list - should be 12 (SR or CR_pass_LOW/SIG/HIGH * 4 years)
        number_new = [i for i in new_split if i == '1.0']
        print(np_name)
        print(old_split)
        print(new_split)
        print(len(number_new))
        if 'mcstats' in np_name:
            assert(len(number_new) == 12)   # should be 12 (SR or CR_pass_LOW/SIG/HIGH * 4 years)
        else: # Xbb mistag, DAK8 tag
            assert(len(number_new) == 24)   # should be 24 (1 region SR or CR) * (2 tagging regions fail/pass) * (3 masks LOW/SIG/HIGH) * (ttbar for 4 years) 
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





#parse_card('card_original.txt')
