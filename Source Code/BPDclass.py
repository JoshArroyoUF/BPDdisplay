# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 20:01:42 2022

@author: joshu
"""

#import copy
#import numpy as np
import itertools
import copy
from collections import defaultdict

class box:
    
    #0 - empty
    #1 - vertical line
    #2 - horizontal line
    #3 - cross
    #4 - se elbow
    #5 - nw elbow
    #6 - bump
    #box location 1-indexed [row, col]
    
    def __init__(self, location, filling):
        self.location = location
        self.filling = filling

class BPD:
    
    #Bumpless Pipe Dream is defined purely by its size and elbow locations
    #Note that elbow locations are 1-indexed!!!
    def __init__(self, size, elbows, reset=0):
        self.size = size
        if reset==0:
            self.latex = ''
        self.elbows = elbows
        self.elbows.sort()
        self.boxes = [box([x,y],0) for x in range(1,self.size+1) for y in range(1,self.size+1)]
        self.pipes = [[] for z in range(self.size)]
        self.bad = []
        self.badpipes = []
        self.nwelbowcount = [0 for z in range(self.size)]
        for i in range(self.size):
            r = self.size
            c = i+1
            dir = 1
            
            while c < self.size+1 and r > 0:
                self.pipes[i].append([r,c])
                boxy = [b for b in self.boxes if b.location == [r,c]]
                
                if [r,c] in self.elbows:
                    if dir==1:
                        if boxy[0].filling  != 0:
                            boxy[0].filling = 6
                        else:
                            boxy[0].filling = 4
                    else:
                        if boxy[0].filling  != 0:
                            boxy[0].filling = 6
                        else:
                            boxy[0].filling = 5
                            self.nwelbowcount[i] += 1
                    dir = -1*dir
                else:
                    if boxy[0].filling  != 0:
                            boxy[0].filling = 3
                    else:
                        if dir==1:
                            boxy[0].filling = 1
                        else:
                            boxy[0].filling = 2
                            
                if dir==1:
                    r += -1
                if dir==-1:
                    c += 1
                if r == 0:
                    self.badpipes.append(self.pipes[i])
                    for pos in self.pipes[i]:
                        self.bad.append(pos)
            
        
        blanks = [b.location for b in self.boxes if b.filling == 0]            
        #self.Schubert = np.array([0]*(self.size-1))
        #for blank in blanks:
        #    self.Schubert[blank[0]-1] += 1
        
        self.perm = []
        for j in range(1,self.size+1):
            permflag = 0
            for i in range(self.size):
                if [j,self.size] == self.pipes[i][len(self.pipes[i])-1] and i not in self.badpipes:
                    permflag = 1
                    self.perm.append(i+1)
                    break
            if permflag == 0:
                self.perm.append('?')
            
            
    def incsize(self,m=1):
        for i in range(m):
            self.elbows.append([self.size+i+1,self.size+i+1])
        self.size += m
            
        self.__init__(self.size,self.elbows,1)
            
    
    #Converts BPD by doing a mindroop move
    #mindroop(BPD,[a,b]) = [a+x,b+y]
    def mindroop(self,location):
        crosses = [b.location for b in self.boxes if b.filling == 3]
        bumps = [b.location for b in self.boxes if b.filling == 6]
        
            
        for x in range(1,self.size-location[0]+2):
            if [location[0]+x,location[1]] not in crosses:
                break
        for y in range(1,self.size-location[1]+2):
            if [location[0],location[1]+y] not in crosses:
                break
            
        if location[0]+x > self.size or location[0]+y > self.size:
            self.incsize()
            
        if [location[0],location[1]] not in bumps:
            self.elbows.remove([location[0],location[1]])
            
        if [location[0]+x,location[1]] in self.elbows:
            self.elbows.remove([location[0]+x,location[1]])
        else:
            self.elbows.append([location[0]+x,location[1]])
        
        if [location[0],location[1]+y] in self.elbows:
            self.elbows.remove([location[0],location[1]+y])
        else:
            self.elbows.append([location[0],location[1]+y])
            
        if [location[0]+x,location[1]+y] not in self.elbows:
            self.elbows.append([location[0]+x,location[1]+y])
        
        self.__init__(self.size,self.elbows,1)
                
        return [location[0]+x,location[1]+y]
    
    #Converts BPD by doing a minundroop move
    #mindroop(BPD,[a,b]) = [a-x,b-y]
    def minundroop(self,location):
        crosses = [b.location for b in self.boxes if b.filling == 3]
        bumps = [b.location for b in self.boxes if b.filling == 6]
        
        for x in range(1,location[0]):
            if [location[0]-x,location[1]] not in crosses:
                break
        for y in range(1,location[1]):
            if [location[0],location[1]-y] not in crosses:
                break
            
        if [location[0],location[1]] not in bumps:
            self.elbows.remove([location[0],location[1]])
            
        if [location[0]-x,location[1]] in self.elbows:
            self.elbows.remove([location[0]-x,location[1]])
        else:
            self.elbows.append([location[0]-x,location[1]])
        
        if [location[0],location[1]-y] in self.elbows:
            self.elbows.remove([location[0],location[1]-y])
        else:
            self.elbows.append([location[0],location[1]-y])
            
        if [location[0]-x,location[1]-y] not in self.elbows:
            self.elbows.append([location[0]-x,location[1]-y])
        
        self.__init__(self.size,self.elbows,1)
        
                
        return [location[0]-x,location[1]-y]
        
    
    #crossbumpswaps if the pipes cross, otherwise changes bump to cross
    def crossbumpswap(self,location):
        self.elbows.remove(location)
        swaploc = location
        crossingpipes = []
        for i in range(self.size):
            if location in self.pipes[i]:
                crossingpipes.append(i)
                self.pipes[i].remove(location)
        for place in self.pipes[crossingpipes[0]]:
            if place in self.pipes[crossingpipes[1]]:
                self.elbows.append(place)
                swaploc = place
                break

        self.__init__(self.size,self.elbows,1)
        
        return swaploc
        
    
    
    def leftinsertionstep(self,biletter,latex=0):
        
        b = biletter[0]
        if b > self.size:
            self.incsize(b-self.size)
        
        k = biletter[1]
        
        i = b
        for t in range(self.size):
            check = [box for box in self.boxes if box.location == [b,t+1] and box.filling == 4]
            if check != []:
                j = t+1
                break
                
        pos = [i,j]
        
        
        flag = 0
        while flag == 0:
            #Step 1
            
            pos = self.mindroop(pos)
            if latex > 0:
                self.tex()
            
            bigcheck = [box for box in self.boxes if box.location == pos]
            
            
            #Step 2
            if bigcheck[0].filling == 5:
                if pos[0] <= k:
                    for t in range(pos[1]+1,self.size+1):
                        check = [box for box in self.boxes if box.location == [pos[0],t] and box.filling == 4]
                        if check != []:
                            pos[1] = t
                            break
                    continue
                    
                else:
                    for t in range(pos[1]-1,0,-1):
                        check = [box for box in self.boxes if box.location == [pos[0],t] and box.filling == 4]
                        if check != []:
                            pos[1] = t
                            break
                    continue
            
            
            #Step 3
            if bigcheck[0].filling == 6:
                
                #a
                
                crossingpipes = []
                for i in range(self.size):
                    if pos in self.pipes[i]:
                        crossingpipes.append(self.pipes[i])
                for p in crossingpipes:
                    if [pos[0],pos[1]-1] not in p:
                        exitrow = p[len(p)-1][0]
                        break
                        
                
                if exitrow <= k:    
                    continue
                
                #b
                else:
                    swappos = self.crossbumpswap(pos)
                
                    if swappos != pos:
                        pos = swappos
                        if latex > 0:
                            self.tex()
                        continue
                    else:
                        flag = 1
                        return self.perm
                    
    
    #perm is the newperm of the BPD moved to.
    def leftuninsertionstep(self,newperm,k,latex=0):
        #Step 0
        crossingpipes = []
        while len(newperm) < len(self.perm):
            newperm.append(len(newperm)+1)
        
        for i in range(len(self.perm)):
            if self.perm[i] != newperm[i]:
                crossingpipes.append(self.pipes[newperm[i]-1])
        crossing = [pos for pos in crossingpipes[0] if pos in crossingpipes[1]]
        pos = crossing[0]
        self.elbows.append(pos)
        self.__init__(self.size, self.elbows,1)
        if latex > 0:
                self.tex()
                
                
                
        flag = 0
        while flag == 0:
            #Step 1
            pos = self.minundroop(pos)
            if latex > 0:
                    self.tex()
                    
            bigcheck = [box for box in self.boxes if box.location == pos]
            #Step 2
            if bigcheck[0].filling == 4:
                #a
                if pos[0] <= k:
                    for j in range(pos[1]-1,0,-1):
                        check = [box for box in self.boxes if box.location == [pos[0],j]]
                        if check[0].filling == 5:
                            pos = [pos[0],j]
                            break
                    else:
                        flag = 1
                        return (pos[0],k)
                #b
                else:
                    for j in range(pos[1],self.size+1):
                        check = [box for box in self.boxes if box.location == [pos[0],j]]
                        if check[0].filling == 5:
                            pos = [pos[0],j]
                            break
                continue
                
            #Step 3
            else:
                #a
                for i in range(self.size):
                    if pos in self.pipes[i]:
                        crossingpipes.append(self.pipes[i])
                for p in crossingpipes:
                    if [pos[0],pos[1]-1] in p:
                        exitrow = p[len(p)-1][0]
                        break
                    
                if exitrow <= k:
                    continue
                    
                #b
                else:
                    pos = self.crossbumpswap(pos)
                    if latex > 0:
                        self.tex()
                    continue
                
    def rightinsertionstep(self,biletter,latex=0):
        
        b = biletter[0]
        if b > self.size:
            self.incsize(b-self.size)
        
        k = biletter[1]
        
        i = b
        for t in range(self.size-1,-1,-1):
            check = [box for box in self.boxes if box.location == [b,t+1] and box.filling == 4]
            if check != []:
                j = t+1
                break
                
        pos = [i,j]
        
        
        flag = 0
        while flag == 0:
            #Step 1
            
            pos = self.mindroop(pos)
            if latex > 0:
                self.tex()
            
            bigcheck = [box for box in self.boxes if box.location == pos]
            
            
            #Step 2
            if bigcheck[0].filling == 5:
                for t in range(pos[1],-1,-1):
                    check = [box for box in self.boxes if box.location == [pos[0],t] and box.filling == 4]
                    if check != []:
                        pos[1] = t
                        break
                continue
            
            if bigcheck[0].filling == 6:
                
                crossingpipes = []
                for i in range(self.size):
                    if pos in self.pipes[i]:
                        crossingpipes.append(self.pipes[i])
                
                crossflag = 0
                for l in crossingpipes[0]:
                    if l != pos and l in crossingpipes[1]:
                        #a
                        pos = self.crossbumpswap(pos)
                        crossflag = 1
                        break
                
                #b
                if crossflag == 0:
                    
                    for p in crossingpipes:
                        if [pos[0],pos[1]-1] not in p:
                            exitrow = p[len(p)-1][0]
                            break
                            
                    if exitrow <= k:    
                        continue
                    
                    else:
                        self.crossbumpswap(pos)
                        flag = 1
                        return self.perm
                    
    
    #perm is the newperm of the BPD moved to.
    def rightuninsertionstep(self,newperm,k,latex=0):
        #Step 0
        crossingpipes = []
        while len(newperm) < len(self.perm):
            newperm.append(len(newperm)+1)
        
        for i in range(len(self.perm)):
            if self.perm[i] != newperm[i]:
                crossingpipes.append(self.pipes[newperm[i]-1])
        crossing = [pos for pos in crossingpipes[0] if pos in crossingpipes[1]]
        pos = crossing[0]
        self.elbows.append(pos)
        self.__init__(self.size, self.elbows,1)
        if latex > 0:
                self.tex()
                
                
                
        flag = 0
        while flag == 0:
            #Step 1
            pos = self.minundroop(pos)
            if latex > 0:
                    self.tex()
                    
            bigcheck = [box for box in self.boxes if box.location == pos]
            #Step 2
            if bigcheck[0].filling == 4:
                finflag = 1
                for j in range(pos[1]+1,self.size+1):
                    check = [box for box in self.boxes if box.location == [pos[0],j]]
                    if check[0].filling == 5:
                        pos = [pos[0],j]
                        finflag = 0
                        break
                if finflag == 1:
                    return (pos[0],k)
                continue
                
            #Step 3
            if bigcheck[0].filling == 6:
                crossingpipes = []
                for i in range(self.size):
                    if pos in self.pipes[i]:
                        crossingpipes.append(self.pipes[i])
                crossflag = 0
                for l in crossingpipes[0]:
                    if l != pos and l in crossingpipes[1]:
                        crossflag = 1
                        break

                #a
                if crossflag == 1:
                    pos = self.crossbumpswap(pos)
                    if latex > 0:
                        self.tex()
                    continue
                
                #b
                else:
                    continue
                    
    
    
    
    #Creates LaTex code to print a BPD
    def tex(self,scale='.4'):
        texcode = '\\begin{tikzpicture}[scale ='+scale+']'
        for b in self.boxes:
            if b.filling == 0:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\nowire};'
            if b.filling == 1:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\vwire};'
            if b.filling == 2:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\hwire};'
            if b.filling == 3:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\cross};'
            if b.filling == 4:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\seelbow};'
            if b.filling == 5:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\nwelbow};'
            if b.filling == 6:
                texcode += '\\node at ('+str(b.location[1]-1)+","+str(self.size-b.location[0])+') {\\bump};'
        
        texcode += '\\end{tikzpicture}'
        
        self.latex += texcode
        
        return texcode
    
def RothaBPD(perm):
    n = len(perm)
    elbows = []
    for i in range(n):
        elbows.append([i+1,perm[i]])
    BumplessPipeDream = BPD(n, elbows)

    return BumplessPipeDream

def permcode(perm):
    c = []
    for i in range(len(perm)):
        c.append(0)
        for j in range(i+1,len(perm)):
            if perm[j] < perm[i]:
                c[i] += 1
    return c

def kcode(perm):
    ks = []
    c = permcode(perm)
    for i in range(len(c)):
        for j in range(c[i]):
            ks.append(i+1)
    return ks

          
def possiblebiwords(kseq):
    size = 1
    kseq.reverse()
    for k in kseq:
        size = size*k
    biwords = []
    biword = []
    for a in range(size):
        if a == 0:
            for k in kseq:
                biword.append([1,k])
        else:
            i = 0
            flag = True
            biword = copy.deepcopy(biword)
            while flag:
                biword[i][0] += 1
                if biword[i][0] > kseq[i]:
                    biword[i][0] = 1
                    i += 1
                else:
                    flag = False
        
        biwords.append(biword)
    return biwords
    
    
#latex = 1 to get all insertions
#latex = 2 to get subinsertions
def leftinsertion(biword,startsize=2,latex=0):
    startperm = [i+1 for i in range(startsize)]
    insertionBPD = RothaBPD(startperm)
    if latex > 0:
        insertionBPD.tex()
    seq = [startperm]
    
    for i in range(len(biword)-1,-1,-1):
        perm = insertionBPD.leftinsertionstep(biword[i],latex-1)
        if latex > 1:
            insertionBPD.tex()
        if latex > 0:
            insertionBPD.latex += '\n\n'
            insertionBPD.tex()
        seq.append(perm)
        
    if latex == 0:
        insertionBPD.tex()
        
    return [insertionBPD, seq]

#latex = 1 to get all insertions
#latex = 2 to get subinsertions
def leftuninsertion(insBPD,ks,perms,latex=0):
    if latex > 0:
        insBPD.tex()
    biword = []
    
    permlen = len(perms[-1])
    for perm in perms:
        while len(perm) < permlen:
            perm.append(len(perm)+1)
    
    for i in range(len(ks)):
        biletter = insBPD.leftuninsertionstep(perms[len(ks)-i-1],ks[i],latex-1)
        biword.append(biletter)
        if latex > 1:
            insBPD.tex()
        if latex > 0:
            insBPD.latex += '\n\n'
            insBPD.tex()
        
    if latex == 0:
        insBPD.tex()
        
    return biword

#latex = 1 to get all insertions
#latex = 2 to get subinsertions
def rightinsertion(biword,startsize=2,latex=0):
    startperm = [i+1 for i in range(startsize)]
    insertionBPD = RothaBPD(startperm)
    if latex > 0:
        insertionBPD.tex()
    seq = [startperm]
    
    for i in range(len(biword)):
        perm = insertionBPD.rightinsertionstep(biword[i],latex-1)
        if latex > 1:
            insertionBPD.tex()
        if latex > 0:
            insertionBPD.latex += '\n\n'
            insertionBPD.tex()
        seq.append(perm)
        
    if latex == 0:
        insertionBPD.tex()
        
    return [insertionBPD, seq]

#latex = 1 to get all insertions
#latex = 2 to get subinsertions
def rightuninsertion(insBPD,ks,perms,latex=0):
    if latex > 0:
        insBPD.tex()
    biword = []
    
    permlen = len(perms[-1])
    for perm in perms:
        while len(perm) < permlen:
            perm.append(len(perm)+1)
    
    for i in range(len(ks)):
        biletter = insBPD.rightuninsertionstep(perms[len(ks)-i-1],ks[len(ks)-i-1],latex-1)
        biword.insert(0,biletter)
        if latex > 1:
            insBPD.tex()
        if latex > 0:
            insBPD.latex += '\n\n'
            insBPD.tex()
        
    if latex == 0:
        insBPD.tex()
        
    return biword


def chain_to_transpositions(chain):
    transpositions = []
    for i in range(len(chain)-1):
        startperm = chain[i]
        endperm = chain[i+1]
        while len(startperm) < len(endperm):
            startperm.append(len(startperm)+1)
        for j in range(len(endperm)):
            if startperm[j] != endperm[j]:
                transpositions.append([startperm[j],endperm[j]])
                break
    return transpositions

def transpositions_to_chain(transpositions):
    chain = [[1,2]]
    for i in range(len(transpositions)):
        chain.append(copy.deepcopy(chain[i]))
        while len(chain[i+1]) < transpositions[i][1]:
            chain[i+1].append(len(chain[i+1])+1)
        swap1 = chain[i+1].index(transpositions[i][0])
        swap2 = chain[i+1].index(transpositions[i][1])
        chain[i+1][swap1] = transpositions[i][1]
        chain[i+1][swap2] = transpositions[i][0]
        
    return chain

def transrules(transpositions, mid): #must have at least 3 transpositions, mid must be at least 1
    v1 = transpositions[mid-1][0]
    v2 = transpositions[mid-1][1]
    v3 = transpositions[mid][0]
    v4 = transpositions[mid][1]
    v5 = transpositions[mid+1][0]
    v6 = transpositions[mid+1][1]
    
    #A forward
    if v1 == v4 == v5:
        #A1 forwards
        if v3 < v1 < v2 < v6:
            transpositions[mid-1] = [v3, v2]
            transpositions[mid] = [v2, v6]
            transpositions[mid+1] = [v1, v2]
        #A2 forward
        elif v3 < v1 < v6 < v2:
            transpositions[mid-1] = [v1, v6]
            transpositions[mid] = [v6, v2]
            transpositions[mid+1] = [v3, v6]
    #A backwards
    elif v2 == v3 == v6:
        #A1 backwards
        if v1 < v5 < v2 < v4:
            transpositions[mid-1] = [v5, v2]
            transpositions[mid] = [v1, v5]
            transpositions[mid+1] = [v5, v4]
        #A2 backwards
        if v5 < v1 < v2 < v4:
            transpositions[mid-1] = [v1, v4]
            transpositions[mid] = [v5, v1]
            transpositions[mid+1] = [v1, v2]
            
    #B1+C1 fowards
    elif v4 < v2 < v6:
        #B1 fowards
        if v3 != v5 and v4 != v5:
            transpositions[mid] = [v5, v6]
            transpositions[mid+1] = [v3, v4]
        #C1 fowards
        elif v4 < v1 and v4 == v5:
            transpositions[mid-1] = [v3, v4]
            transpositions[mid] = [v5, v6]
            transpositions[mid+1] = [v1, v2]
            
    #B1+C2 backwards
    elif v6 < v2 < v4:
        #B1 backwards
        if v5 != v3 and v6 != v3:
            transpositions[mid] = [v5, v6]
            transpositions[mid+1] = [v4, v5]
        #C2 backwards
        elif v6 < v1 and v6 == v3:
            transpositions[mid-1] = [v3, v4]
            transpositions[mid] = [v5, v6]
            transpositions[mid+1] = [v1, v2]
            
    #B2+C2 fowards
    elif v4 < v6 < v2:
        #B2 forwards
        if v3 != v1 and v4 != v1:
            transpositions[mid-1] = [v3, v4]
            transpositions[mid] = [v1, v2]
        #C2 fowards
        elif v4 < v5 and v1 == v4:
            transpositions[mid-1] == [v5, v6]
            transpositions[mid] == [v1, v2]
            transpositions[mid+1] == [v3, v4]
            
    #B2+C1 backwards
    elif v2 < v6 < v4:
        #B2 backwards
        if v1 != v3 and v2 != v3:
            transpositions[mid-1] = [v3, v4]
            transpositions[mid] = [v1, v2]
        #C1 backwards
        elif v2 < v5 and v2 == v3:
            transpositions[mid-1] = [v5, v6]
            transpositions[mid] = [v1, v2]
            transpositions[mid] = [v3, v4]
            
    return transpositions
            
print(transrules([[3,4],[2,5],[1,2]],1))