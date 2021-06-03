#!/usr/bin/python3
#!echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
#!mpiexec --oversubscribe -n 10 python3 mpi_echo.py
#!mpirun --oversubscribe -n 10 python3 mpi_echo.py
# modified echo algorithm
# -->a father knows his children
# -->nodes exchange messages in the Stree to
# --> calculate hops and distance from root for each node
#and the height of STree 

from mpi4py import MPI
import queue

comm = MPI.COMM_WORLD
wsize = comm.Get_size()
rank = comm.Get_rank()
cnt,cnt1=0,0
STree=[]

if (wsize >= 3):
    # print(wsize,rank)
    index = [0 for _ in range(wsize)]
    edges = [0 for _ in range(13*wsize)]
    neighbours = [0 for x in range(10*wsize)]
    
    #indexes and edges of the 3 graphs 
    #comment 2 and left the others uncomment
    # 1rst graph
    index=[2,5,6,9,12,15,18,21,24,26]
    edges=[1,4,0,2,3,1,1,4,5,0,3,6,3,6,7,4,5,8,5,8,9,6,7,9,7,8]
    #2nd graph
    # index=[2,4,6,9,11,14,17,19,21,23]
    # edges=[1,3,0,2,5,7,0,4,5,3,6,3,6,2,4,5,8,2,9,6,9,7,8]
    #3nd graph
    # index=[2,4,7,10,13,16,20,22,24,26]
    # edges=[1,2,0,3,0,5,6,1,4,6,3,6,9,2,6,7,2,3,4,5,5,8,7,9,4,8]

#create graph with 10 nodes with the above indexes and edges
    g = comm.Create_graph(index, edges)
#start echo from initiator node with rank ==0 
#the initiator will be the root of spanning tree
#build spanning tree 
    if (rank == 0): #Initiator send message to his neighbors
        neighbourNumber = g.Get_neighbors_count(rank)
        neighbours = g.Get_neighbors(rank)
        print("initiator node number is = "+str(rank)+" and has "+str(neighbourNumber)+" neighbours")
        print("-------------------------------------")
        cnt1=1
        for i in range(neighbourNumber):
            print("Node: ",neighbours[i],'distance from root',cnt1)
            print("-------------------------------------")
        print("Spanning Tree traversal starts:",flush=True)
        print("-------------------------------------")
        #cnt, send tokens to every neighbour
        for k in range (neighbourNumber):
            #send distance to next node
            data=('token send from initiator:',rank,'--> : ',neighbours[k],"hops from root -->:",cnt)
            comm.send(data, dest = neighbours[k])
           #wait for a response from evey neighbour of initiator
        for k in range(neighbourNumber):
            request = comm.irecv(source = neighbours[k])  #non-blocking receive
            token = request.wait()
    else: #continue with the other nodes which are non-initiators 
        status = MPI.Status()
        token = comm.recv(source=MPI.ANY_SOURCE, status=status) #blocking reveice message from any source
        print("STree traversal started from root",token[0:5],token[5]+1,flush=True)
        
        father = status.Get_source()
        STree.append(father)
        STree.append(token[2:4])
        cnt+=token[5]+1  #increase cnt distance from root
        if (rank==9) :
            print("STree branch: ",STree,"Height of Spanning Tree :",cnt)
        else:
            print("STree branch: ",STree,"||--> node {} has distance from root of STree :".format(token[3]),cnt)
        #Printout children of the father
        print("node {} ".format(father),"has {} as child".format(rank))
        #send token to all neighbours except father
        neighbourNumber = g.Get_neighbors_count(rank)
        neighbours = g.Get_neighbors(rank)
        for k in range(neighbourNumber):
            if (neighbours[k] != father):
                #cnt, send distance to nect node
                data=('token send from :',rank,'--> : ',neighbours[k],"hops from root -->:",cnt)
                comm.send(data, dest = neighbours[k])
                
        for k in range (neighbourNumber):
            if (neighbours[k] != father):
                request = comm.irecv(source = neighbours[k])    #non-blocking receive 
                token = request.wait()

        data=('token send from :',rank,'to : ',neighbours[k])        
        comm.send(data, dest = father)
        
        print("Node " + str(rank) + " has node " + str(father) + " as father")
        print("-------------------------------------")
