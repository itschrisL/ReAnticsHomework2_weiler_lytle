import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from SearchTree import *
from StateNode import *


##
# AIPlayer
# Description: The responsibility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Better Random")
        self.searchTree = SearchTree()
        self.searchTree.depthLimit = 2

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        self.searchTree.top = StateNode(currentState, None, None, None, 0)
        self.searchTree.top.subNodes = self.RecursiveFindMove(currentState, 0)
        bestScore = 0
        bestNode = self.searchTree.top
        for node in self.searchTree.top.subNodes:
            if node.score > bestScore:
                bestNode = node
                bestScore = node.score

        return bestNode.move


    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass


    def RecursiveFindMove(self, GameState, currentDepth):
        if currentDepth <= self.searchTree.depthLimit:
            nodes = []
            states = []  # List of next states being generated by each move
            currentDepth += 1

            node = StateNode(GameState, None, 0, None, currentDepth, None, None)

            moves = listAllLegalMoves(GameState)  # List of all legal moves from that state

            for move in moves:
                states.append(getNextState(GameState, move))

            for i in range(0, len(states)):
                evalScore = self.calculateStateScore(states[i])
                newNode = StateNode(states[i], GameState, evalScore, moves[i], currentDepth, node, None)
                nodesToCalculate = self.RecursiveFindMove(states[i], currentDepth)
                if nodesToCalculate is not None:
                    newNode.subNodes = nodesToCalculate
                    node.score = self.evaluateNodeList(nodesToCalculate)
                nodes.append(newNode)
            return nodes
        else:
            return None



    # Evaluates a list of nodes and
    #
    def evaluateNodeList(self, nodes):
        if nodes is not None:
            sum = 0
            for node in nodes:
                if node is not None:
                    sum += node.score
            average = sum/(len(nodes))
            return average
        else:
            return 0  # meaning no nodes in list

    def calculateStateScore(self, currentState):
        rtrnNumber = \
            self.hasPlaerWon(currentState) + \
            self.numOfAnts(currentState) + \
            self.numOfFood(currentState) + \
            self.myQueeenThreat(currentState) + \
            self.enemyQueenThreat(currentState) + \
            self.workerAnts(currentState)
        print(rtrnNumber)
        return rtrnNumber

    ##
    # If there is enemy ants close to my queen
    #
    def myQueeenThreat(self, currentState):
        myID = currentState.whoseTurn
        enemyID = 1 - myID

        myInv = currentState.inventories[myID]
        enemyInv = currentState.inventories[enemyID]

        queenCords = myInv.getQueen().coords
        enemyAnts = enemyInv.ants
        closestAnt = None
        for ant in enemyAnts:
            if ant.type is not QUEEN and ant.type is not WORKER:
                if closestAnt is None:
                    closestAnt = ant

                if approxDist(ant.coords, queenCords) < approxDist(closestAnt.coords, queenCords):
                    closestAnt = ant
        if closestAnt is None:
            rtrnNumber = 0
        else:
            rtrnNumber = -0.5 / approxDist(closestAnt.coords, queenCords)
        print("Queen Threat: " + str(rtrnNumber))
        return rtrnNumber

    ##
    # If one of my ants is close to the enemy queen
    #
    def enemyQueenThreat(self, currentState):
        myID = currentState.whoseTurn
        enemyID = 1 - myID

        myInv = currentState.inventories[myID]
        enemyInv = currentState.inventories[enemyID]

        enemyQueenCords = enemyInv.getQueen().coords
        myAnts = myInv.ants
        if len(myAnts) is not 0:
            closestAnt = myAnts[0]
            for ant in myAnts:
                if ant.type is not QUEEN and ant.type is not WORKER:
                    if approxDist(ant.coords, enemyQueenCords) < approxDist(closestAnt.coords, enemyQueenCords):
                        closestAnt = ant

        if closestAnt.type is not QUEEN and closestAnt.type is not WORKER:
            rtrnNumber = 0.5 / approxDist(closestAnt.coords, enemyQueenCords)
        else:
            rtrnNumber = 0.00

        print("Enemy Queen Threat: " + str(rtrnNumber))
        return rtrnNumber

    def hasPlaerWon(self, currentState):
        if getWinner(currentState) is None:
            return 0.0
        elif getWinner(currentState) == 1:
            return 1.0
        elif getWinner(currentState) == 0:
            return -1.0

    def numOfAnts(self, currentState):
        myInv = currentState.inventories[self.playerId]
        myAnts = myInv.ants

        enemyInv = getEnemyInv(self, currentState)
        enemyAnts = enemyInv.ants

        difference = len(myAnts) - len(enemyAnts)
        rtrnNumber = difference * 0.05
        print("Number of Ants: " + str(rtrnNumber))
        return rtrnNumber

    ##
    # numOfFood
    #
    # Calculates the amount of food that the human has
    def numOfFood(self, currentState):
        enemyFood = getEnemyInv(self, currentState).foodCount
        myFood = len(getCurrPlayerFood(self, currentState))

        difference = (myFood - enemyFood)
        rtrnNumber = difference * 0.05
        print("Food Count: " + str(rtrnNumber))
        return rtrnNumber

    def workerAnts(self, currentState):
        me = currentState.whoseTurn
        foods = getConstrList(currentState, None, (FOOD,))
        myFood = foods[0]
        myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        myWorkers = getAntList(currentState, me, (WORKER,))
        rtrnNumber = 0
        dist = 0
        if len(myWorkers) is not 0:
            for worker in myWorkers:
                if worker.carrying:
                    dist += approxDist(worker.coords, myTunnel.coords)
                else:
                    dist += approxDist(worker.coords, myFood.coords)
                rtrnNumber += 0.05/dist
        print("Worker Ants: " + str(rtrnNumber))
        return rtrnNumber
