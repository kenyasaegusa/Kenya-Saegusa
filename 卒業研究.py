import random as rd 
import matplotlib.pyplot as plt
import math
import copy
import time
import numpy as np
service_radius=5000
#number_of_customers=50
number_of_customers = 100
number_of_trucks=100
#number_of_drones = 4
number_of_drones = 8
using_drone = 0
using_truck = 0
cost_min = 30
cost_max = 60
truck_capacity = 300
truck_cost = 300
truck_speed = 400
drone_capacity = 100
drone_cost = 100
drone_speed = 600
#drone_customers = 20
drone_customers = 40
destroy_number = 3
#トラックの時間に関するペナルティ
time_penalty = 1000
#トラックの台数に関するペナルティ
truck_penalty = 1000000
#削除した顧客を記憶する配列
destroy_node = []


""""
def setup ():
    plt.rcParams["figure.figsize"] = (10,10)
    x=[0] #put deport (start point) at the middle of service area
    y=[0]   
    c=[0]
    for i in range (1,number_of_customers+1):
        x.append(int(rd.uniform(-service_radius,service_radius)))
        y.append(int(rd.uniform(-service_radius,service_radius)))
        c.append(int(rd.uniform(cost_min,cost_max)))
    #実際には存在しない点を用意
    x.append(100)
    y.append(100)
    c.append(1000000000)
    return(x,y,c)
"""
def setup ():
    plt.rcParams["figure.figsize"] = (10,10)
    x=[0] #put deport (start point) at the middle of service area
    y=[0]   
    c=[0]
    rd.seed(9)
    for i in range (1,number_of_customers+1):
        x.append(int(rd.uniform(-service_radius,service_radius)))
        y.append(int(rd.uniform(-service_radius,service_radius)))
        c.append(int(rd.uniform(cost_min,cost_max)))
    #実際には存在しない点を用意
    x.append(1000000000)
    y.append(10000000)
    c.append(1000000000)
    return(x,y,c)

def show (x,y):
    plt.scatter(x[0],y[0], s=100, c='r')     
    for i in range (1,drone_customers+1):
        plt.scatter(x[i],y[i], s=50, c='g')
    for i in range(drone_customers, number_of_customers + 1):
           plt.scatter(x[i],y[i], s=50, c='b') 
    for i in range(1, number_of_customers + 1):
        plt.text(x[i],y[i] + 50, i , ha='center')

#改訂版visualize
def visualize(route):
    show (x,y)
    color=['black','brown','deeppink','blueviolet','orange','aqua','Gray','red','c','purple']
    j=0
    for i in range (0,using_truck):
        j+=1
        if j>=len(color):
            j=0
        for k in range(0,len(route[i])-1):        
            plt.plot([x[route[i][k]],x[route[i][k+1]]],[y[route[i][k]],y[route[i][k+1]]],color[j]) 
    for i in range (using_truck,len(route)):
        for k in range(0,len(route[i])-1):
            plt.plot([x[route[i][k]],x[route[i][k+1]]],[y[route[i][k]],y[route[i][k+1]]],'lime') 
    plt.show()

"""
#改訂版visualize
def visualize(route):
    show (x,y)
    color=['black','brown','deeppink','blueviolet','orange','aqua','Gray','red','c','purple']
    j=0
    for i in range (0,using_truck):
        j+=1
        if j>=len(color):
            j=0
        for k in range(0,len(route[i])-1):        
            plt.annotate('', xy=[y[route[i][k]],y[route[i][k+1]]], xytext=[x[route[i][k]],x[route[i][k+1]]],
                arrowprops=dict(shrink=0, width=1, headwidth=8, 
                                headlength=10, connectionstyle='arc3',
                                facecolor='gray', edgecolor='gray')
               )
    for i in range (using_truck,len(route)):
        for k in range(0,len(route[i])-1):
            plt.plot([x[route[i][k]],x[route[i][k+1]]],[y[route[i][k]],y[route[i][k+1]]],'lime') 
    plt.show()
"""
def distance(i,j):
    return math.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)

#ルートとトラックの台数を与えて時間のリストを作る
def time_setting(route,using_truck):
    time1 = copy.deepcopy(route)
    #print("route:",route)
    for i in range(0,using_truck):
        for k in range(1,len(route[i])):
            time1[i][k] = time1[i][k-1] + distance(route[i][k-1],route[i][k])/truck_speed
    for i in range(using_truck,len(route)):
        if route[i][0] == 0:
            pass
        else:
            for k in range(0,using_truck):
                if route[i][0] in route[k]:
                    l = route[k].index(route[i][0])
                    time1[i][0] = time1[k][l]
        for m in range(1,len(route[i])):
            time1[i][m] = time1[i][m-1] + distance(route[i][m-1],route[i][m])/drone_speed
    for i in range(using_truck,len(route)):
        if route[i][-1] == 0:
            pass
        else:
            for k in range(0,using_truck):
                if route[i][-1] in route[k]:
                    l = route[k].index(route[i][-1])
                    if time1[k][l] < time1[i][-1]:
                        increase_time = time1[i][-1] - time1[k][l]
                        for m in range(l,len(route[k])):
                            time1[k][l] = time1[k][l] + increase_time
    return time1

#時間tにおける着陸する候補の頂点を返す関数(ドローンノード以外)
def next_truck_node(route,t):
    time1 = time_setting(route,using_truck)
    node = []
    for i in range(0,using_truck):
        a = True
        for j in range(0,len(route[i])):
            if a == True:
                if t < time1[i][j]:
                    if route[i][j] > drone_customers:
                        node.append(route[i][j])
                        a = False
                        break
    if node == []:
        node = [0]

    return(node)

#時間tににおける発射地点の候補を返す関数
def launch_truck_node(route,t):
    time1 = time_setting(route,using_truck)
    node = []
    for i in range(0,using_truck):
        a = True
        for j in range(0,len(route[i])):
            if a == True:
                if t > time1[i][len(route[i])-j-1]:
                    if route[i][len(route[i])-j-1] > drone_customers:
                        node.append(route[i][len(route[i])-j-1])
                        a = False
    if node == []:
        node = [0]
    return(node)

#頂点のリストを与えて一番近い頂点の番号を出力する関数
def nearest_node(node_list,current_node):
    if node_list == []:
        print("空が呼び出されています")
    min_distance = 10000000
    number = 0
    if node_list == []:
        number = number_of_customers + 1
    else:
        for i in range(0,len(node_list)):
            if min_distance > distance(node_list[i],current_node):
                min_distance = distance(node_list[i],current_node)
                number = node_list[i]
    
    return(number)

#時間のリストを与えて最も小さい値をもつリストの番号を返す関数
def min_time_drone(drone_time):
    time1 = 100000000000
    for i in range(0,len(drone_time)):
        if time1 > drone_time[i][len(drone_time[i])-1]:
            time1 = drone_time[i][len(drone_time[i])-1]
            number = i

    return(number)

#時間tまでにトラックで訪れられるドローンノードを返す関数
def truck_drone_node(time1,t):
    node = []
    for i in range(0,using_truck):
        #ルートiにおいて時間tを下回るインデックスの番号
        number = 0
        j = 0
        while number == 0 and j < len(time1[i])-1:
            j = j + 1
            if time1[i][j] > t:
                number = j
        node.append(j - 1)
    return(node)

#頂点nodeの時間を調べる関数
def node_time(route,node):
    time1 = time_setting(route,using_truck)
    for i in range(0,len(route)):
        if node in route[i]:
            j = route[i].index(node)
            return time1[i][j]
            break

def first_truck_route():
    global using_truck
    using_truck = 0
    all_customer = []
    route = []
    for i in range(drone_customers+1,number_of_customers+1):
        all_customer.append(i)
    current_node = 0
    while all_customer != []:
        add_customer = nearest_node(all_customer,current_node)
        if using_truck == 0:
            using_truck = 1
            route.append([0,add_customer,0])
            all_customer.remove(add_customer)
            current_node = add_customer
        else:
            if route_cost(route,using_truck-1) + c[add_customer] <= truck_capacity:
                change_route = route[using_truck-1]
                change_route.insert(len(change_route)-1,add_customer)
                route[using_truck-1] = change_route
                all_customer.remove(add_customer)
                current_node = add_customer
            else:
                add_customer = nearest_node(all_customer,0)
                using_truck = using_truck + 1
                route.append([0,add_customer,0])
                all_customer.remove(add_customer)
                current_node = add_customer
    return route

def first_add_drone(route):
    customer = []
    drone_location = []
    global using_drone
    for i in range(1,drone_customers + 1):
        customer.append(i)
    for i in range(number_of_drones):
        using_drone = using_drone + 1
        cost = 0
        first_node = nearest_node(customer,0)
        customer.remove(first_node)
        service_time = distance(0,first_node)/drone_speed
        cost = c[first_node]
        second_node = nearest_node(customer,first_node)
        if cost + c[second_node] > drone_capacity:
            return_option = next_truck_node(route,service_time)
            return_node = nearest_node(return_option,first_node)
            route.append([0,first_node,return_node])  
            drone_location.append(return_node)          
        else:
            service_time = service_time + distance(first_node,second_node)/drone_speed
            customer.remove(second_node)
            cost = cost + c[second_node]
            third_node = nearest_node(customer,second_node)
            if cost + c[third_node] > drone_capacity:
                return_option = next_truck_node(route,service_time)
                return_node = nearest_node(return_option,second_node)
                route.append([0,first_node,second_node,return_node])
                drone_location.append(return_node)
            else:
                service_time = service_time + distance(second_node,third_node)/drone_speed
                return_option = next_truck_node(route,service_time)
                return_node = nearest_node(return_option,third_node)
                customer.remove(third_node)
                route.append([0,first_node,second_node,third_node,return_node])
                drone_location.append(return_node)

    while customer != [] and drone_location != []:
        j = 100 * 10
        for i in range(len(drone_location)):
            if node_time(route,drone_location[i]) < j:
                launch_node = drone_location[i]
                j = node_time(route,drone_location[i])
        drone_location.remove(launch_node)
        first_node = nearest_node(customer,launch_node)
        customer.remove(first_node)
        service_time = node_time(route,launch_node) + distance(first_node,launch_node) / drone_speed
        cost = c[first_node]
        if customer == []:
            return_option = next_truck_node(route,service_time)
            return_node = nearest_node(return_option,first_node)
            route.append([launch_node,first_node,return_node])
        else:
            second_node = nearest_node(customer,first_node)
            cost = cost + c[second_node]
            if cost > drone_capacity:
                return_option = next_truck_node(route,service_time)
                return_node = nearest_node(return_option,first_node)
                route.append([launch_node,first_node,return_node])
                if return_node != 0:
                    drone_location.append(return_node)
            else:
                customer.remove(second_node)
                service_time = service_time + distance(first_node,second_node) / drone_speed
                if customer == []:
                    return_option = next_truck_node(route,service_time)
                    return_node = nearest_node(return_option,second_node)
                    route.append([launch_node,first_node,second_node,return_node])
                else:
                    third_node = nearest_node(customer,second_node)
                    cost = cost + c[third_node]
                    if cost > drone_capacity:
                        return_option = next_truck_node(route,service_time)
                        return_node = nearest_node(return_option,second_node)
                        route.append([launch_node,first_node,second_node,return_node])
                        if return_node != 0:
                            drone_location.append(return_node)
                    else:
                        customer.remove(third_node)
                        service_time = service_time + distance(second_node,third_node) / drone_speed
                        return_option = next_truck_node(route,service_time)
                        return_node = nearest_node(return_option,third_node)
                        route.append([launch_node,first_node,second_node,third_node,return_node])
                        if return_node != 0:
                            drone_location.append(return_node)
    
    if customer != []:
        global using_truck
        current_node = 0
        while customer != []:
            add_customer = nearest_node(customer,current_node)
            if route_cost(route,using_truck-1) + c[add_customer] <= truck_capacity:
                change_route = route[using_truck-1]
                change_route.insert(len(change_route)-1,add_customer)
                route[using_truck-1] = change_route
                customer.remove(add_customer)
                current_node = add_customer
            else:
                add_customer = nearest_node(customer,0)
                using_truck = using_truck + 1
                route.append([0,add_customer,0])
                customer.remove(add_customer)
                current_node = add_customer
    return route
        
                
                    

                





#出発したドローンが同じトラックに帰ってくるかを表す関数
def return_same_truck(route,route_of_drone):
    if route_of_drone[0] == 0:
        return True
    else:
        for i in range(0,using_truck):
            if route_of_drone[0] in route[i]:
                if route_of_drone[-1] in route[i]:
                    return True
                else:
                    return False
                break
            else:
                pass

#着陸したドローンの次のドローンルートを出力する関数(ない場合は{0}を出力)
def next_drone_route(route,return_node):
    for i in range(0,using_truck):
        if return_node in route[i]:
            for j in range(route[i].index(return_node),len(route[i])-1):
                for k in range(using_truck,len(route)):
                    if route[i][j] == route[k][0]:
                        return route[k]
                        break
                    else:
                        pass
        else:
            pass
    return 0

#コストの値を計算する
def number_of_cost(route_number,i,m,n):
    if  route_number < using_truck:
        return (distance(i,m) + distance(m,n) - distance(i,n)) * truck_cost
    else:
        return (distance(i,m) + distance(m,n) - distance(i,n)) * drone_cost


#ドローンルートの最終地点を出力する関数
def last_drone_node(route,using_truck):
    last_node = []
    node_list = []
    for i in range(using_truck,len(route)):
        node_list.append([route[i][0],route[i][-1]])
    while node_list != []:
        min_time = 100000000000
        for i in range(0,len(node_list)):
            if min_time > node_time(route,node_list[i][0]):
                j = i
                min_time = node_time(route,node_list[i][0])
        while j != -1:
            return_node = node_list[j][1]
            if return_node == 0:
                node_list.pop(j)
                last_node.append(0)
                j = -1
            else:
                node_list.pop(j)
                j = -1
                for a in range(0,using_truck):
                    if return_node in route[a]:
                        number = route[a].index(return_node)
                        for b in range(number,len(route[a])-1):
                            for c in range(0,len(node_list)):
                                if route[a][b] == node_list[c][0]:
                                    j = c
                                    break
                if j == -1:
                    last_node.append(return_node)
    return (last_node)

#ドローンの最初の地点を出力する
def first_drone_node(route,using_truck):
    first_node = []
    node_list = []
    for i in range(using_truck,len(route)):
        node_list.append([route[i][0],route[i][-1]])
    while node_list != []:
        max_time = 0
        for i in range(0,len(node_list)):
            if max_time <= node_time(route,node_list[i][-1]):
                j = i
                max_time = node_time(route,node_list[i][-1])
        #print("j0",j)
        while j != -1:
            launch_node = node_list[j][0]
            if launch_node == 0:
                node_list.pop(j)
                first_node.append(0)
                j = -1
            else:
                node_list.pop(j)
                j = -1
                for a in range(0,using_truck):
                    if launch_node in route[a]:
                        number = route[a].index(launch_node)
                        for b in range(1,number+1):
                            for c in range(0,len(node_list)):
                                if route[a][b] == node_list[c][-1]:
                                    j = c
                                    break
                if j == -1:
                    first_node.append(launch_node)
    return (first_node)
        
#指定されたノードからドローンを発射できるかを表す関数
def launch_possibility(route,using_truck,number):
    node = last_drone_node(route,using_truck)
    for i in range(0,using_truck):
        if number in route[i]:
            a = route[i].index(number)
            for j in range(0,a+1):
                if route[i][j] in node:
                    return True
                    break
    
#指定されたノードにドローンが戻れるかを表す関数
def return_possibility(route,using_truck,number):
    node = first_drone_node(route,using_truck)
    for i in range(0,using_truck):
        if number in route[i]:
            a = route[i].index(number)
            for j in range(a,len(route[i])-1):
                if route[i][j] in node:
                    return True
                    break

#ルートのコストを出す関数
def route_cost(route,i):
    cost = 0
    for j in range(1,len(route[i])):
        cost = cost + c[route[i][j]]
    return cost

    
    


#指定した顧客を削除する
def destroy(number):
    global destroy_node
    i = 0
    global using_truck
    while i < using_truck:
        if number in route[i]:
            if len(route[i]) == 3:
                using_truck = using_truck - 1
                route.pop(i)
            else:
                route[i].remove(number)
            break
        i = i + 1
    #ドローンルートを調べる
    i = using_truck
    while i < len(route):
        if number in route[i]:
            #発着のトラックが同じかどうか
            if return_same_truck(route,route[i]) == True:
                if len(route[i]) == 3:
                    if route[i].index(number) == 0 or route[i].index(number) == 2:
                        destroy_node.append(route[i][1])
                    route.pop(i)
                    i = i -1
                else:
                    if route[i][0] == number or route[i][-1] == number:
                        for k in range(1,len(route[i])-1):
                            destroy_node.append(route[i][k])
                        route.pop(i)
                        i = i -1
                    else:
                        route[i].remove(number)
            else:

                if len(route[i]) == 3 or route[i].index(number) == 0 or route[i].index(number) == len(route[i])-1:
                    #削除するルートがドローンルートの初めのルートかを調べる
                    for a in range(0,using_truck):
                        if route[i][0] in route[a]:
                            b = route[a].index(route[i][0])
                            x = 0
                            for c in range(0,b+1):
                                for d in range(using_truck,len(route)):
                                    global using_drone
                                    if route[a][c] == route[d][-1] and route[a][c] != 0:
                                        x = 1
                            if x == 0:
                                using_drone = using_drone - 1
                            
                                    
                        
                    return_node = route[i][-1]
                    for k in range(1,len(route[i])-1):
                        destroy_node.append(route[i][k])
                    route.pop(i)
                    i = i-1
                    for l in range(0,len(route)-using_truck):
                        if next_drone_route(route,return_node) == 0:
                            break
                        else:
                            next_route = next_drone_route(route,return_node)
                            return_node = next_route[-1]
                            remove_number = route.index(next_route)
                            for m in range(1,len(route[remove_number])-1):
                                destroy_node.append(route[remove_number][m])
                            route.remove(next_route)
                else:
                    route[i].remove(number)   
        else:
            pass
        i = i + 1

    i = 0
    while i < len(destroy_node):
        j = i + 1
        while j < len(destroy_node):
            if destroy_node[i] == destroy_node[j]:
                destroy_node.pop(j)
            else:
                j = j + 1
        i = i + 1
    return (route)
#ランダム削除
def D1(route,number):
    global destroy_node
    all_customer = []
    for i in range(0,len(route)):
        for k in range(1,len(route[i])-1):
            all_customer.append(route[i][k])
    d = []
    global iteration_number
    rd.seed(iteration_number)
    for i in range(number):
        k = int(rd.uniform(0,len(all_customer))) 
        d.append(all_customer[k])
        all_customer.pop(k)
    for i in range(len(d)):
        destroy_node.append(d[i])
        route = destroy(d[i])
    return route

#Shaw destroy(ランダムに選んだ点から最も近い点をi個削除する)
def D2(route,destroy_number):
    all_customer = []
    for i in range(0,len(route)):
        for k in range(1,len(route[i])-1):
            all_customer.append(route[i][k])
    #print("all_customer:",all_customer)
    global iteration_number
    rd.seed(iteration_number)
    number = int(rd.uniform(0,len(all_customer))) 
    #print("all_customer:",all_customer)
    first_destroy = all_customer[number]
    global destroy_node
    destroy_node.append(first_destroy)
    all_customer.remove(first_destroy)
    for k in range(0,destroy_number):
        node = nearest_node(all_customer,first_destroy)
        destroy_node.append(node)
        all_customer.remove(node)
    a = set(destroy_node)
    destroy_node = list(a)
    i = 0
    while i < len(destroy_node):
        #print("destroy_node1:",destroy_node)
        #print("destroy_node[i]",destroy_node[i])
        route = destroy(destroy_node[i])
        i = i + 1
    return route

#Worst Destroy(コストが最も大きい点をnumber個削除する)
def D3(route,number):
    cost_list = [[0,-10000]]
    for j in range(0,len(route)):
        for k in range(1,len(route[j]) -1):
            cost = number_of_cost(j,route[j][k-1],route[j][k],route[j][k+1])
            a = True
            iteration = 0
            while a == True: 
                if cost_list[iteration][-1] < cost:
                    cost_list.insert(iteration,[route[j][k],cost])
                    a = False
                else:
                    iteration = iteration + 1
    for i in range(number):
        destroy_node.append(cost_list[i][0])
        route = destroy(cost_list[i][0])
    return route

#number個のドローンルートを削除する
def D4(route,number):
    for i in range(0,number):
        k = int(rd.uniform(using_truck,len(route)))
        for l in range(1,len(route[k])-1):
            global destroy_node
            destroy_node.append(route[k][l])
            route = destroy(route[k][l])

    return route

#number個のトラックルートをランダムに削除する
def D5(route,number):
    for i in range(0,number):
        k = int(rd.uniform(0,using_truck))
        l = 1
        m = len(route[k])-1
        while l < m:
            global destroy_node
            destroy_node.append(route[k][1])
            route = destroy(route[k][1])
            l = l + 1
    return route

#到着が最も遅いトラックルートを削除する
def D6(route):
    truck_time = time_setting(route,using_truck)
    return_time = 0
    for i in range(using_truck):
        if return_time < truck_time[i][-1]:
            k = i
    l = 1
    m = len(route[k])-1
    while l < m:
        global destroy_node
        destroy_node.append(route[k][1])
        route = destroy(route[k][1])
        l = l + 1
    return route
    
"""
#ドローンにインサートする関数
def drone_insert(route,number):
    launch_option = []
    node = last_drone_node(route,using_truck)
    #ドローンが使いきれていない場合
    global using_drone
    if using_drone < number_of_drones:
        using_drone = using_drone + 1
        all_customer = [0]
        for i in range(0,using_truck):
            for j in range(1,len(route[i])-1):
                all_customer.append(route[i][j])
        launch_node = nearest_node(all_customer,number)
        service_time = node_time(route,launch_node) + distance(launch_node,number) / drone_speed
        return_option = next_truck_node(route,service_time)
        return_node = nearest_node(return_option,number)
        objective_route = copy.deepcopy(route)
        objective_route.append([launch_node,number,return_node])
        return objective_route
    else:
        #新たにドローンを発射できる集合
        for i in range(0,using_truck):
            for j in range(0,len(node)):
                if node[j] in route[i]:
                    k = route[i].index(node[j])
                    for l in range(k,len(route[i])-1):
                        launch_option.append(route[i][l])
        a = set(launch_option)
        launch_option = list(a)
        if 0 in launch_option:
            launch_option.remove(0)
        for i in range(using_truck,len(route)):
            for j in range(1,len(route[i])-1):
                launch_option.append(route[i][j])
        a = 0
        while a == 0:
            node = nearest_node(launch_option,number)
            if launch_option == []:
                a = 1
                return truck_insert(route,number)

            else:
                if node <= drone_customers:
                    for i in range(using_truck,len(route)):
                        if node in route[i] and route[i].index(node) != 0 and route[i].index(node) != len(route[i])-1:
                            cost = 0
                            for j in range(1,len(route[i])):
                                cost = cost + c[route[i][j]]
                            if cost + c[number] <= drone_capacity:
                                k = route[i].index(node)
                                if distance(number,route[i][k-1]) < distance(number,route[i][k+1]):
                                    objective_route = copy.deepcopy(route)
                                    change_route = objective_route[i]
                                    change_route.insert(k,number)
                                    objective_route[i] = change_route
                                else:
                                    objective_route = copy.deepcopy(route)
                                    change_route = objective_route[i]
                                    change_route.insert(k+1,number)
                                    objective_route[i] = change_route
                                a = 1
                                return objective_route
                            else:
                                for j in range(1,len(route[i])-1):
                                    #print("launch_option:",launch_option)
                                    #print("node",node)
                                    #print("route[i]:",route[i])
                                    #print("len(route[i])",len(route[i]))
                                    launch_option.remove(route[i][j])

                    for i in range(0,using_truck):
                        if node in route[i]:
                            launch_time = node_time(route,node)
                            service_time = launch_time + distance(node,number) / drone_speed
                            return_option = next_truck_node(route,service_time)
                            return_node = nearest_node(return_option,number)
                            objective_route = copy.deepcopy(route)
                            objective_route.append([node,number,return_node])
                            a = 1
                            return objective_route
                else:
                    launch_time = node_time(route,node)
                    service_time = launch_time + distance(node,number) / drone_speed
                    return_option = next_truck_node(route,service_time)
                    return_node = nearest_node(return_option,number)
                    objective_route = copy.deepcopy(route)
                    objective_route.append([node,number,return_node])
                    a = 1
                    return objective_route
"""
#ドローンにinsertする関数
def drone_insert2(route,number):
    launch_option = []
    node = last_drone_node(route,using_truck)
    #ドローンが使いきれていない場合
    global using_drone
    if using_drone < number_of_drones:
        using_drone = using_drone + 1
        all_customer = [0]
        for i in range(0,using_truck):
            for j in range(1,len(route[i])-1):
                all_customer.append(route[i][j])
        launch_node = nearest_node(all_customer,number)
        service_time = node_time(route,launch_node) + distance(launch_node,number) / drone_speed
        return_option = next_truck_node (route,service_time)
        return_node = nearest_node(return_option,number)
        objective_route = copy.deepcopy(route)
        objective_route.append([launch_node,number,return_node])
        return objective_route
    else:
        all_customer = []
        for i in range(len(route)):
            for j in range(1,len(route[i])-1):
                all_customer.append(route[i][j])
        a =False
        iteration = 0
        while a == False and iteration < 10:
            node = nearest_node(all_customer,number)
            for i in range(len(route)):
                if node in route[i]:
                    l = i
                    break
            if l < using_truck:
                if launch_possibility(route,using_truck,node) == True:
                    a = True
                    service_time = node_time(route,node) + distance(node,number) / drone_speed
                    return_option = next_truck_node(route,service_time)
                    return_node = nearest_node(return_option,number)
                    route.append([node,number,return_node])
                else:
                    if return_possibility(route,using_truck,node) == True:
                        a = True
                        service_time = node_time(route,node) - distance(node,number) / drone_speed
                        launch_option = launch_truck_node(route,service_time)
                        launch_node = nearest_node(launch_option,number)
                        route.append([launch_node,number,node])
                    else:
                        all_customer.remove(node)
                        iteration = iteration + 1
            else:
                if route_cost(route,l) + c[number] <= drone_capacity:
                    a = True
                    k = route[l].index(node)
                    change_route = route[l]
                    if distance(number,route[l][k-1]) < distance(number,route[l][k+1]):
                        change_route.insert(k,number)
                    else:
                        change_route.insert(k+1,number)
                    route[l] = change_route
                else:
                    for m in range(1,len(route[l])-1):
                        all_customer.remove(route[l][m])
                    iteration = iteration + 1
        if a == False:
            route = truck_insert(route,number)
    return route

def drone_insert(route,number):
    global using_drone
    all_customer = []
    for i in range(len(route)):
        for j in range(1,len(route[i])-1):
            all_customer.append(route[i][j])
    a = False
    iteration = 0
    while a == False and all_customer != [] and iteration < 10:
        node = nearest_node(all_customer,number)
        for i in range(len(route)):
            if node in route[i]:
                k = i
                break
        if k < using_truck:
            if launch_possibility(route,using_truck,node) == True:
                a = True
                service_time = node_time(route,node) + distance(node,number) / drone_speed
                return_option = next_truck_node(route,service_time)
                return_node = nearest_node(return_option,number)
                route.append([node,number,return_node])
            else:
                if return_possibility(route,using_truck,node) == True:
                    a = True
                    service_time = node_time(route,node) - distance(node,number) / drone_speed
                    launch_option = launch_truck_node(route,service_time)
                    launch_node = nearest_node(launch_option,number)
                    route.append([launch_node,number,node])
                else:
                    if using_drone < number_of_drones:
                        a = True
                        using_drone = using_drone + 1
                        service_time = node_time(route,node) + distance(node,number) / drone_speed
                        return_option = next_truck_node(route,service_time)
                        return_node = nearest_node(return_option,number)
                        route.append([node,number,return_node])
                    else:
                        all_customer.remove(node)           
        else:
            if route_cost(route,k) + c[number] <= drone_cost:
                a = True
                l = route[k].index(node)
                change_route = route[k]
                if distance(route[k][l-1],number) < distance(route[k][l+1],number):
                    change_route.insert(l,number)
                else:
                    change_route.insert(l+1,number)
                route[k] = change_route
            else:
                for i in range(1,len(route[k])-1):
                    """
                    if route[k][i] in all_customer:
                        pass
                    else:
                        print(route)
                        print(all_customer)
                        print(route[k][i])
                        print(node)
                        print(route_possibility(route))
                    """
                    all_customer.remove(route[k][i])
        iteration = iteration + 1
    if a == False:
        route = truck_insert(route,number)
    return route

#トラックにinsertする関数
def truck_insert(route,number):
    all_customer = []
    global using_truck
    for i in range(0,using_truck):
        for j in range(1,len(route[i])-1):
            all_customer.append(route[i][j])
    a = 0
    while a == 0:
        if all_customer == []:
            objective_route = copy.deepcopy(route)
            objective_route.insert(0,[0,number,0])
            using_truck = using_truck + 1
            a = 1
        else :
            node = nearest_node(all_customer,number)
            for i in range(0,using_truck):
                if node in route[i]:
                    cost = 0
                    for j in range(1,len(route[i])-1):
                        cost = cost + c[route[i][j]]
                    if cost + c[number] <= truck_capacity:
                        k = route[i].index(node)
                        if distance(route[i][k-1],number) < distance(route[i][k+1],number):
                            objective_route = copy.deepcopy(route)
                            change_route = objective_route[i]
                            change_route.insert(k,number)
                            objective_route[i] = change_route
                        else: 
                            objective_route = copy.deepcopy(route)
                            change_route = objective_route[i]
                            change_route.insert(k+1,number)
                            objective_route[i] = change_route
                        a = 1
                    else:
                        for j in range(1,len(route[i])-1):
                            all_customer.remove(route[i][j])
                
    return objective_route


#目的関数値を計算
def objective_function(route,using_truck):
    time1 = time_setting(route,using_truck)
    value = 0
    for i in range(0,using_truck):
        for j in range(1,len(route[i])):
            value = value +distance(route[i][j-1],route[i][j]) * truck_cost
    for i in range(using_truck,len(route)):
        for j in range(1,len(route[i])):
            value = value + distance(route[i][j-1],route[i][j]) * drone_cost
    for i in range(0,using_truck):
        value = value + time1[i][-1] * time_penalty
    value = value + using_truck * truck_penalty
    return value
"""

#目的関数値を計算
def objective_function(route,using_truck):
    time1 = time_setting(route,using_truck)
    value = 0
    for i in range(0,using_truck):
        for j in range(1,len(route[i])):
            value = value +distance(route[i][j-1],route[i][j]) * truck_cost
    for i in range(using_truck,len(route)):
        for j in range(1,len(route[i])):
            value = value + distance(route[i][j-1],route[i][j]) * drone_cost
    return value
"""
#ルートの書き換えとcost_listの更新
def remove_node(route,cost_list_number):
    global cost_list
    global using_truck
    number = cost_list[cost_list_number][0]
    if len(route[cost_list[cost_list_number][1]]) == 3:
        route.pop(cost_list[cost_list_number][1])
        using_truck = using_truck - 1
        for j in range(len(cost_list)):
            if cost_list[j][1] > cost_list[cost_list_number][1]:
                cost_list[j][1] = cost_list[j][1] - 1
    else:
        change_route = route[cost_list[cost_list_number][1]]
        change_route.remove(cost_list[cost_list_number][0])
        route[cost_list[cost_list_number][1]] = change_route
        for j in range(len(cost_list)):
            for k in range(cost_list[cost_list_number][2],len(route[cost_list[cost_list_number][1]])):
                if cost_list[j][0] == route[cost_list[cost_list_number][1]][k]:
                    cost_list[j][2] = cost_list[j][2] - 1
    for i in range(len(cost_list)):
        if cost_list[i][0] == number:
            cost_list.pop(i)
            break
    return route

#着陸ノードの決定
def decide_return_node(route,cost_list_number):
    if route[cost_list[cost_list_number][1]][cost_list[cost_list_number][2]+ 1] > drone_customers:
        return route[cost_list[cost_list_number][1]][cost_list[cost_list_number][2]+ 1]
    else:
        if route[cost_list[cost_list_number][1]][cost_list[cost_list_number][2]- 1] > drone_customers:
            return route[cost_list[cost_list_number][1]][cost_list[cost_list_number][2]- 1]
        else:
            truck_node = []
            for i in range(drone_customers + 1, number_of_customers + 1):
                truck_node.append(i)
            return nearest_node(truck_node,cost_list[cost_list_number][0])




def add_drone_route(route):
    global using_drone
    global using_truck
    global cost_list
    global drone_list
    truck_node = []
    for i in range(drone_customers+1,number_of_customers+1):
        truck_node.append(i)
    
    #ドローン顧客のコストリストを作る
    cost_list = []
    drone_list = []
    for i in range(1,drone_customers+1):
        for j in range(using_truck):
            if i in route[j]:
                a = True
                for k in range(using_truck + 1,len(route)):
                    if i in route[k]:
                        a = False
                        break
                if a == True:
                    drone_list.append(i)
                    number = route[j].index(i)
                    cost = distance(route[j][number-1],i) + distance(route[j][number+1],i)
                    if cost_list == []:
                        cost_list.append([i,j,number,cost])
                    else:
                        k = 0
                        l = True
                        while k < len(cost_list) and l == True:
                            if cost_list[k][-1] < cost:
                                cost_list.insert(k,[i,j,number,cost])
                                l = False
                            else:
                                k = k + 1
                        if l == True:
                            cost_list.append([i,j,number,cost])

    #使われていないドローンでルートを生成
    number = number_of_drones - using_drone
    for i in range(number):
        if cost_list == []:
            break
        else:
            first_node = cost_list[0][0]
            drone_list.remove(first_node)
            if route[cost_list[0][1]][cost_list[0][2]-1] > drone_customers:
                launch_node = route[cost_list[0][1]][cost_list[0][2]-1]
            else:
                launch_node = nearest_node(truck_node,first_node)
            if drone_list == []:
                service_time = node_time(route,launch_node) + distance(launch_node,first_node) / drone_speed
                return_option = next_truck_node(route,service_time)
                k = 0
                while k < len(return_option):
                    if return_option[k] <= drone_customers:
                        return_option.pop(k)
                    else:
                        k = k + 1
                if return_option == []:
                    return_option = [0]
                return_node = nearest_node(return_option,first_node)
                route.append([launch_node,first_node,return_node])
                route = remove_node(route,0)
            else:
                second_node = nearest_node(drone_list,first_node)
                cost = c[first_node] + c[second_node]
                service_time = node_time(route,launch_node) + distance(launch_node,first_node) / drone_speed
                if cost <= drone_capacity:
                    service_time = service_time + distance(second_node,first_node) / drone_speed
                    drone_list.remove(second_node)
                    route = remove_node(route,0)
                    if drone_list == []:
                        return_option = next_truck_node(route,service_time)
                        k = 0
                        while k < len(return_option):
                            if return_option[k] <= drone_customers:
                                return_option.pop(k)
                            else:
                                k = k + 1
                        if return_option == []:
                            return_option = [0]
                        return_node = nearest_node(return_option,second_node)
                        route.append([launch_node,first_node,second_node,return_node])
                        for j in range(0,len(cost_list)):
                                if cost_list[j][0] == second_node:
                                    a = j
                        route = remove_node(route,a)
                    else:
                        third_node = nearest_node(drone_list,second_node)
                        cost = cost + c[third_node]
                        for j in range(0,len(cost_list)):
                            if cost_list[j][0] == second_node:
                                a = j
                        if cost <= drone_capacity:
                            service_time = service_time + distance(second_node,third_node) / drone_speed
                            drone_list.remove(third_node)
                            route = remove_node(route,a)
                            for j in range(0,len(cost_list)):
                                if cost_list[j][0] == third_node:
                                    a = j
                            return_option = next_truck_node(route,service_time)
                            k = 0
                            while k < len(return_option):
                                if return_option[k] <= drone_customers:
                                    return_option.pop(k)
                                else:
                                    k = k + 1
                            if return_option == []:
                                return_option = [0]
                            return_node = nearest_node(return_option,third_node)
                            route.append([launch_node,first_node,second_node,third_node,return_node])
                            route = remove_node(route,a)
                        else:
                            return_option = next_truck_node(route,service_time)
                            k = 0
                            while k < len(return_option):
                                if return_option[k] <= drone_customers:
                                    return_option.pop(k)
                                else:
                                    k = k + 1
                            if return_option == []:
                                return_option = [0]
                            return_node = nearest_node(return_option,second_node)
                            route.append([launch_node,first_node,second_node,return_node])
                            route = remove_node(route,a)
                else:
                    return_option = next_truck_node(route,service_time)
                    k = 0
                    while k < len(return_option):
                        if return_option[k] <= drone_customers:
                            return_option.pop(k)
                        else:
                            k = k + 1
                    if return_option == []:
                        return_option = [0]
                    return_node = nearest_node(return_option,first_node)
                    route.append([launch_node,first_node,return_node])
                    route = remove_node(route,0)
    using_drone = number_of_drones
    #新たなドローンルートの生成
    while cost_list != []:
        first_node = cost_list[0][0]
        drone_list.remove(first_node)
        launch_option = copy.copy(truck_node)
        a = True
        while a == True and launch_option != []:
            b = nearest_node(launch_option,first_node)
            if launch_possibility(route,using_truck,b) == True:
                launch_node = b
                a = False
            else:
                launch_option.remove(b)
        if a == True:
            cost_list = []
        else:
            service_time = node_time(route,launch_node) + distance(launch_node,first_node) / drone_speed
            if drone_list == []:
                return_option = next_truck_node(route,service_time)
                k = 0
                while k < len(return_option):
                    if return_option[k] <= drone_customers:
                        return_option.pop(k)
                    else:
                        k = k + 1
                if return_option == []:
                    return_option = [0]
                return_node = nearest_node(return_option,first_node)
                route.append([launch_node,first_node,return_node])
                route = remove_node(route,0)
            else:
                second_node = nearest_node(drone_list,first_node)
                cost = c[first_node] + c[second_node]
                if cost <= drone_capacity:
                    service_time = service_time + distance(second_node,first_node) / drone_speed
                    drone_list.remove(second_node)
                    route = remove_node(route,0)
                    for j in range(0,len(cost_list)):
                        if cost_list[j][0] == second_node:
                            a = j
                    if drone_list == []:
                        return_option = next_truck_node(route,service_time)
                        k = 0
                        while k < len(return_option):
                            if return_option[k] <= drone_customers:
                                return_option.pop(k)
                            else:
                                k = k + 1
                        if return_option == []:
                            return_option = [0]
                        return_node = nearest_node(return_option,second_node)
                        route.append([launch_node,first_node,second_node,return_node])
                        route = remove_node(route,a)
                    else:
                        third_node = nearest_node(drone_list,second_node)
                        cost = cost + c[third_node]
                        if cost <= drone_capacity:
                            service_time = service_time + distance(third_node,second_node) / drone_speed
                            route = remove_node(route,a)
                            drone_list.remove(third_node)
                            for j in range(0,len(cost_list)):
                                if cost_list[j][0] == third_node:
                                    a = j
                            return_option = next_truck_node(route,service_time)
                            k = 0
                            while k < len(return_option):
                                if return_option[k] <= drone_customers:
                                    return_option.pop(k)
                                else:
                                    k = k + 1
                            if return_option == []:
                                return_option = [0]
                            return_node = nearest_node(return_option,third_node)
                            route.append([launch_node,first_node,second_node,third_node,return_node])
                            route = remove_node(route,a)
                        else:
                            return_option = next_truck_node(route,service_time)
                            k = 0
                            while k < len(return_option):
                                if return_option[k] <= drone_customers:
                                    return_option.pop(k)
                                else:
                                    k = k + 1
                            if return_option == []:
                                return_option = [0]
                            return_node = nearest_node(return_option,second_node)
                            route.append([launch_node,first_node,second_node,return_node])
                            route = remove_node(route,a)
                else:
                    return_option = next_truck_node(route,service_time)
                    k = 0
                    while k < len(return_option):
                        if return_option[k] <= drone_customers:
                            return_option.pop(k)
                        else:
                            k = k + 1
                    if return_option == []:
                        return_option = [0]
                    return_node = nearest_node(return_option,first_node)
                    route.append([launch_node,first_node,return_node])
                    route = remove_node(route,0)
    return route

"""
#コストが最も小さい点に挿入する
def R1(route):
    global destroy_node
    global using_truck
    global using_drone
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(0,len(destroy_node)):
        if destroy_node[i] > drone_customers:
            all_customer =[]
            add = False
            while all_customer != [] and add == False:
                for j in range(0,using_truck):
                    for k in range(1,len(route[j])-1):
                        all_customer.append(route[j][k])
                node = nearest_node(all_customer,destroy_node[i])
                for j in range(using_truck):
                    if node in route[j]:
                        number = j
                if route_cost(route,number) + c[destroy_node[i]] <= truck_capacity:
                    k = route[number].index(node)
                    if distance(route[number][k-1]) <= distance(route[number][k+1]):
                        change_route = route[number]
                        change_route.insert(k,destroy_node[i])
                        route[number] = change_route
                        add = True
                    else:
                        change_route = route[number]
                        change_route.insert(k+1,destroy_node[i])
                        route[number] = change_route
                        add = True
                else:
                    for k in range(1,len(route[number])-1):
                        all_customer.remove(route[number][k])

        else:
            if using_drone < number_of_drones:
                using_drone = using_drone + 1
                truck_customer = []
                for j in range(0,using_truck):
                    for k in range(1,len(route[j])-1):
                        truck_customer.append(route[j][k])
                launch_node = nearest_node(truck_customer,destroy_node[i])
                service_time = node_time(route,launch_node) + distance(launch_node,destroy_node[i]) / drone_speed
                return_option = next_truck_node(route,service_time)
                return_node = nearest_node(return_option,destroy_node[i])
                route.append([launch_node,destroy_node[i],return_node])
                add = True
            else:
                truck_customer = []
                for j in range(0,using_truck):
                    for k in range(1,len(route[j])-1):
                        truck_customer.append(route[j][k])
                drone_customer = []
                for j in range(using_truck,len(route)):
                    for k in range(1,len(route[j])-1):
                        drone_customer.append(route[j][k])
                add = False
                while add == False and truck_customer != [] and drone_customer != []:
                    truck_node = nearest_node(truck_customer,destroy_node[i])
                    drone_node = nearest_node(drone_customer,destroy_node[i])
                    if launch_possibility(route,using_truck,truck_node) == True or return_possibility(route,using_truck,truck_node) == True:
                        if distance(destroy_node[i],truck_node) >= distance(destroy_node[i],drone_node):
                            for j in range(using_truck,len(route)):
                                if drone_node in route[j]:
                                    number = j
                            if route_cost(route,j) + c[destroy_node[i]] <= drone_capacity:
                                k = route[number].index(drone_node)
                                if distance(route[number][k-1],destroy_node[i]) <= distance(route[number][k+1],destroy_node[i]):
                                    change_route = route[number]
                                    change_route.insert(k,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                                else:
                                    change_route = route[number]
                                    change_route.insert(k+1,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                            else:
                                for k in range(1,len(route[number])-1):
                                    drone_customer.remove(route[number][k])
                        else:
                            if launch_possibility(route,using_truck,truck_node) == True:
                                service_time = node_time(route,truck_node) + distance(truck_node,destroy_node[i]) / drone_speed
                                return_option = next_truck_node(route,service_time)
                                return_node = nearest_node(return_option,destroy_node[i])
                                route.append([truck_node,destroy_node[i],return_node])
                                add = True
                            else:
                                service_time = node_time(route,truck_node) - distance(truck_node,destroy_node[i]) / drone_speed
                                launch_option = launch_truck_node(route,service_time)
                                launch_node = nearest_node(launch_option,destroy_node[i])
                                route.append([launch_node,destroy_node[i],truck_node])
                                add = True

                    else:
                        if distance(truck_node,destroy_node[i]) * truck_cost <= distance(drone_node,destroy_node[i]) * drone_cost:
                            for j in range(using_truck):
                                if truck_node in route[j]:
                                    number = j
                            if route_cost(route,number) + c[destroy_node[i]] <= truck_capacity:
                                k = route[number].index(truck_node)
                                if distance(route[number][k-1],destroy_node[i]) <= distance(route[number][k+1],destroy_node[i]):
                                    change_route = route[number]
                                    change_route.insert(k,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                                else:
                                    change_route = route[number]
                                    change_route.insert(k+1,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                            else:
                                for k in range(1,len(route[number])-1):
                                    truck_customer.remove(route[number][k])
                        else:
                            for j in range(using_truck,len(route)):
                                if drone_node in route[j]:
                                    number = j
                            if route_cost(route,j) + c[destroy_node[i]] <= drone_capacity:
                                k = route[number].index(drone_node)
                                if distance(route[number][k-1],destroy_node[i]) <= distance(route[number][k+1],destroy_node[i]):
                                    change_route = route[number]
                                    change_route.insert(k,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                                else:
                                    change_route = route[number]
                                    change_route.insert(k+1,destroy_node[i])
                                    route[number] = change_route
                                    add = True
                            else:
                                for k in range(1,len(route[number])-1):
                                    drone_customer.remove(route[number][k])
        if add == False:
            route.insert(using_truck,[0,destroy_node[i],0])
            using_truck = using_truck + 1
    destroy_node = []
    return route
"""

#greedy法
def R1(route):
    global destroy_node
    global using_truck
    global using_drone
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(0,len(destroy_node)):
        all_customer = [0]
        for j in range(len(route)):
            for k in range(1,len(route[j])-1):
                all_customer.append(route[j][k])
        truck_customer = [0]
        for j in range(using_truck):
            for k in range(1,len(route[j])-1):
                truck_customer.append(route[j][k])
        a = True
        if destroy_node[i] <= drone_customers:
            while a == True and all_customer != []:
                node = nearest_node(all_customer,destroy_node[i])
                if node != 0:
                    for j in range(len(route)):
                        if node in route[j]:
                            number = j
                            break
                    if number < using_truck:
                        if launch_possibility(route,using_truck,node) == True:
                            service_time = node_time(route,node) + distance(node,destroy_node[i]) / drone_speed
                            return_option = next_truck_node(route,service_time)
                            return_node = nearest_node(return_option,destroy_node[i])
                            route.append([node,destroy_node[i],return_node])
                            a = False
                        else:
                            if return_possibility(route,using_truck,node) == True:
                                service_time = node_time(route,node) - distance(node,destroy_node[i]) / drone_speed
                                launch_option = launch_truck_node(route,service_time)
                                launch_node = nearest_node(launch_option,destroy_node[i])
                                route.append([launch_node,destroy_node[i],node])
                                a = False
                            else:
                                if using_drone < number_of_drones:
                                    service_time = node_time(route,node) + distance(node,destroy_node[i]) / drone_speed
                                    return_option = next_truck_node(route,service_time)
                                    return_node = nearest_node(return_option,destroy_node[i])
                                    route.append([node,destroy_node[i],return_node])
                                    a = False
                                    using_drone = using_drone + 1
                                else:
                                    if route_cost(route,number) + c[destroy_node[i]] <= truck_capacity:
                                        b = route[number].index(node)
                                        change_route = route[number]
                                        if distance(route[number][b-1],destroy_node[i]) < distance(route[number][b+1],destroy_node[i]):
                                            change_route.insert(b,destroy_node[i])
                                            route[number] = change_route
                                        else:
                                            change_route.insert(b+1,destroy_node[i])
                                            route[number] = change_route
                                        a = False
                                    else:
                                        for j in range(1,len(route[number])-1):
                                            all_customer.remove(route[number][j])
                    else:
                        if route_cost(route,number) + c[destroy_node[i]] <= drone_capacity:
                            b = route[number].index(node) 
                            change_route = route[number]
                            if distance(route[number][b-1],destroy_node[i]) < distance(route[number][b+1],destroy_node[i]):
                                change_route.insert(b,destroy_node[i])
                                route[number] = change_route
                            else:
                                change_route.insert(b+1,destroy_node[i])
                                route[number] = change_route
                            a = False
                        else:
                            for j in range(1,len(route[number])-1):
                                #print(route)
                                #print(route[number])
                                #print(all_customer)
                                all_customer.remove(route[number][j])
                else:
                    option = []
                    for j in range(using_truck):
                        if route_cost(route,j) + c[destroy_node[i]] <= truck_capacity:
                            option.append(route[j][1])
                            option.append(route[j][-2])
                    if option != []:
                        node = nearest_node(option,destroy_node[i])
                        for j in range(using_truck):
                            if node in route[j]:
                                change_route = route[j]
                                if route[j].index(node) == 1:
                                    change_route.insert(1,destroy_node[i])
                                else:
                                    change_route.insert(len(route[j])-1,destroy_node[i])
                                route[j] = change_route
                    else:
                        route.insert(0,[0,destroy_node[i],0])
                        using_truck = using_truck + 1
                    a = False
        else:
            while truck_customer != [] and a == True:
                node = nearest_node(truck_customer,destroy_node[i])
                if node != 0:
                    for j in range(using_truck):
                        if node in route[j]:
                            number = j
                            break
                    if route_cost(route,number) + c[destroy_node[i]] <= truck_capacity:
                        b = route[number].index(node)
                        change_route = route[number]
                        if distance(route[number][b-1],destroy_node[i]) < distance(route[number][b+1],destroy_node[i]):
                            change_route.insert(b,destroy_node[i])
                        else:
                            change_route.insert(b+1,destroy_node[i])
                        route[number] = change_route
                        a = False
                    else:
                        for j in range(1,len(route[number])-1):
                            truck_customer.remove(route[number][j])
                else:
                    option = []
                    for j in range(using_truck):
                        if route_cost(route,j) + c[destroy_node[i]] <= truck_capacity:
                            option.append(route[j][1])
                            option.append(route[j][-2])
                    if option != []:
                        node = nearest_node(option,destroy_node[i])
                        for j in range(using_truck):
                            if node in route[j]:
                                change_route = route[j]
                                if route[j].index(node) == 1:
                                    change_route.insert(1,destroy_node[i])
                                else:
                                    change_route.insert(len(route[j])-1,destroy_node[i])
                                route[j] = change_route
                    else:
                        route.insert(0,[0,destroy_node[i],0])
                        using_truck = using_truck + 1
                    a = False 
    destroy_node = []
    return route

#ドローンノードをドローンルートに挿入後トラックルートに挿入
def R4(route):
    global destroy_node
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(0,len(destroy_node)):
        if destroy_node[i] <= drone_customers:
            route = drone_insert(route,destroy_node[i])
        else:
            route = truck_insert(route,destroy_node[i])
    destroy_node = []
    return route



#トラックルートに挿入後ドローンルートを生成する
def R3(route):
    global destroy_node
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(0,len(destroy_node)):
        route = truck_insert(route,destroy_node[i])
    route = add_drone_route(route)
    destroy_node = []
    return route

#ドローンノードをドローンルートに挿入後トラックルートに挿入
def R2(route):
    global destroy_node
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(len(destroy_node)):
        if destroy_node[i] > drone_customers:
            route = truck_insert(route,destroy_node[i])
    for i in range(len(destroy_node)):
        if destroy_node[i] <= drone_customers:
            route = drone_insert(route,destroy_node[i])
    destroy_node = []
    return route
"""
#トラックルートに挿入した後にドローンルートを生成する
def R3(route):
    global destroy_node
    a = set(destroy_node)
    destroy_node = list(a)
    for i in range(0,len(destroy_node)):
        route = truck_insert(route,destroy_node[i])
    destroy_node = []
    drone_truck_route = []
    for i in range(0,using_truck):
        for j in range(1,len(route[i])-1):
            if route[i][j] <= drone_customers:
                drone_truck_route.append(route[i][j])
    launch_option = []
    return_option = []
    return_node = first_drone_node(route,using_truck)
    for i in range(0,len(return_node)):
        for j in range(0,using_truck):
            if return_node[i] in route[j]:
                number = route[j].index(return_node[i])
                for k in range(1,number+1):
                    return_option.append(route[j][k])
    a = set(return_option)
    return_option = list(a)
    i = 0
    while i < len(return_option):
        if return_option[i] <= drone_customers:
            return_option.remove(return_option[i])
        else:
            i = i+1
    launch_node = last_drone_node(route,using_truck)
    for i in range(0,len(launch_node)):
        for j in range(0,using_truck):
            if launch_node[i] in route[j]:
                number = route[j].index(launch_node[i])
                for k in range(1,number+1):
                    launch_option.append(route[j][k])
    a = set(launch_option)
    launch_option = list(a)
    i = 0
    while i < len(launch_option):
        if launch_option[i] <= drone_customers:
            launch_option.remove(launch_option[i])
        else:
            i = i+1
    option = return_option + launch_option
    for i in range(0,len(drone_truck_route)):
        objective_route = copy.deepcopy(route)
        if option == []:
            pass
        else:
            for j in range(0,using_truck):
                if drone_truck_route[i] in route[j]:
                    route_number = j
                    number = route[j].index(drone_truck_route[i])
                    current_cost = (distance(route[j][number-1],route[j][number]) + distance(route[j][number],route[j][number+1])) * truck_cost
            node = nearest_node(option,drone_truck_route[i])
            if node in launch_option:
                service_time = node_time(route,node) + distance(node,drone_truck_route[i])/drone_speed
                return_customer = nearest_node(next_truck_node(route,service_time),drone_truck_route[i])
                cost = (distance(node,drone_truck_route[i]) + distance(drone_truck_route[i],return_customer)) * drone_cost
                if cost < current_cost:
                    objective_route = copy.deepcopy(route)
                    change_route = objective_route[route_number]
                    change_route.remove(drone_truck_route[i])
                    objective_route[route_number] = change_route
                    objective_route.append([node,drone_truck_route[i],return_customer])
                    for k in range(1,len(route[route_number])):
                        if route[route_number][k] in option:
                            option.remove(route[route_number][k])
                else:
                    global using_drone
                    if using_drone < number_of_drones:
                        objective_route = copy.deepcopy(route)
                        objective_route.append([node,drone_truck_route[i],return_customer])
                        using_drone = using_drone + 1
            else:
                service_time = node_time(route,node) - distance(node,drone_truck_route[i])/drone_speed
                if service_time < 1:
                    service_time = 1
                launch_customer = nearest_node(launch_truck_node(route,service_time),drone_truck_route[i])
                cost = (distance(node,drone_truck_route[i]) + distance(drone_truck_route[i],launch_customer)) * drone_cost
                if cost < current_cost:
                    objective_route = copy.deepcopy(route)
                    change_route = objective_route[route_number]
                    change_route.remove(drone_truck_route[i])
                    objective_route[route_number] = change_route
                    objective_route.insert(using_truck+1,[launch_customer,drone_truck_route[i],node])
                    for k in range(1,len(route[route_number])):
                        if route[route_number][k] in option:
                            option.remove(route[route_number][k])
                else:
                    if using_drone < number_of_drones:
                        objective_route = copy.deepcopy(route)
                        objective_route.insert(using_truck+1,[launch_customer,drone_truck_route[i],node])
                        using_drone = using_drone + 1
                    
            route = copy.deepcopy(objective_route)
    return route
"""
"""
#ランダムな位置に挿入する
def R4(route):
    global destroy_node
    global using_truck
    a = set(destroy_node)
    destroy_node = list(a)
    for a in range(0,len(destroy_node)):
        if destroy_node[a] <= drone_customers:
            b = 0
            while b < 10:
                b = b + 1
                i = int(rd.uniform(0,len(route)))
                if i < using_truck:
                    if route_cost(route,i) + c[destroy_node[a]] <= truck_capacity:
                        j = int(rd.uniform(1,len(route[i])))
                        b = 100
                        change_route = route[i]
                        change_route.insert(j,destroy_node[a])
                        route[i] = change_route
                else:
                    if route_cost(route,i) + c[destroy_node[a]] <= drone_capacity:
                        j = int(rd.uniform(1,len(route[i])))
                        b = 100
                        change_route = route[i]
                        change_route.insert(j,destroy_node[a])
                        route[i] = change_route
            if b != 100:
                using_truck = using_truck + 1
                route.insert(0,[0,destroy_node[a],0])
        else:
            b = 0
            while b < 8:
                b = b + 1
                i = int(rd.uniform(0,using_truck))
                if route_cost(route,i) + c[destroy_node[a]] <= truck_capacity:
                    j = int(rd.uniform(1,len(route[i])))
                    b = 100
                    change_route = route[i]
                    change_route.insert(j,destroy_node[a])
                    route[i] = change_route
                
            if b != 100:
                using_truck = using_truck + 1
                route.insert(0,[0,destroy_node[a],0])
    destroy_node = []
    return route
"""


def route_possibility(route):
    possibility = True
    all_customer = []
    for i in range(1,number_of_customers+1):
        all_customer.append(i)
    for i in range(0,len(route)):
        for j in range(1,len(route[i]) -1):
            all_customer.remove(route[i][j])
    if all_customer != []:
        possibility = False
        print("顧客が足りていない")
    for i in range(using_truck,len(route)):
        for j in range(1,len(route[i])-1):
            if route[i][j] > drone_customers:
                possibility = False
                print("ドラック顧客にドローンで配送")
    for i in range(using_truck):
        if route[i][0] != 0 or route[i][-1] != 0:
            possibility = False
            print("using_truckの数が合っていない")
    c = True
    for i in range(using_truck,len(route)):
        a = False
        b = False
        for j in range(0,using_truck):
            if route[i][0] in route[j]:
                a = True
            if route[i][-1] in route[j]:
                b = True
        if a == False or b == False:
            c = False
    if c == False:
            possibility = False
            print("ドローンの発着点がトラックルートにない")
    for i in range(using_truck,len(route)):
        for j in range(1,len(route[i])-1):
            for k in range(len(route)):
                if route[i][j] in route[k] and k != i:
                    possibility = False
                    print("ドローンノードが2回登場している")
                    print("2回登場しているのは",route[i][j])
                    print("登場場所は",(i,k))
                    print(route)
    for i in range(len(route)):
        for j in range(len(route[i])):
            if 0 <= route[i][j] <= number_of_customers:
                pass
            else:
                possibility = False
                print("範囲外の顧客が登場している")
                print("範囲外の顧客は",route[i][j])
    
    return possibility
                

   
start = time.perf_counter()
x,y,c=setup()
route = first_truck_route()
route = first_add_drone(route)
print(route)
print(route_possibility(route))
#print(using_drone)
#result=greedy()
#route = truck_route()
#time1 = truck_time()
#using_truck = len(route)
#print("Truck_route", route)
#print("using_trick:",using_truck)
#using_drone = number_of_drones
#(route,time1) = add_drone()
first_route = copy.deepcopy(route)
first_using_truck = using_truck
first_using_drone = using_drone
#print("route:",route)
#print("last_drone_node:",last_drone_node(route,using_truck))
#print("目的間数値",objective_function(route,using_truck))
#print("ドローンの使用台数",using_drone)
#print("Truck_time", time1)
#print("Truck_route", route)
time1 = time_setting(route,using_truck)
#print("Truck_time",time1)
#route = destroy(19)

#(route,destroy_node) = D1(route,2)

#print(destroy_node)

#(route,destroy_node) = D2(route)
#(route,destroy_node) = D2(route)
#print("route:",route)
#print("using_truck:",using_truck)
#(route) = R1(route)
#print("destroy_node:",destroy_node)
objective_value = objective_function(route,using_truck)
print("first_value:",objective_value)
#print("objedctive_value:",objective_value)

"""
iteration_number = 0
while iteration_number < 100:
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    (route) = D4(route,2)
    (route) = R2(route)
    if objective_value > objective_function(route,using_truck):
        objective_value = objective_function(route,using_truck)
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone
    a = 0

    iteration_number = iteration_number + 1
print(route)
print(route_possibility(route))

"""

def repair_decide(a,b,c):
    i = int(a)
    j = int(b)
    k = int(c)
    global iteration_number
    rd.seed(iteration_number)
    x = int(rd.uniform(1,i + j + k + 1))
    if x <= i:
        return 1
    elif x <= i + j:
        return 2
    else:
        return 3

def destroy_decide(a,b):
    i = int(a)
    j = int(b)
    global iteration_number
    rd.seed(iteration_number)
    x = int(rd.uniform(1,i + j + 1))
    if x <= i:
        return 1
    else:
        return 2
#A = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#A = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40]
A = [0,1,2,3,4,5,6,7,8,9,10]
"""
iteration_number = 0
route = copy.deepcopy(first_route)
using_truck = first_using_truck
using_drone = first_using_drone
objective_value = objective_function(route,using_truck)
n1 = []
start1 = time.perf_counter()
time_number = 0
first_number = 0
second_number = 0
third_number = 0
while time_number <= 300:
#while iteration_number <= 100:
    now = time.perf_counter()
    if now - start1 > time_number:
        time_number = time_number + 15
        n1.append(objective_value)
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    #print("destroy_node",destroy_node)
    if iteration_number % 2 == 0:
        route = D1(route,3)
    else:
        route = D2(route,2)
    decide_number = repair_decide(first_number,second_number,third_number)
    if decide_number == 1:
        route = R1(route)
    elif decide_number == 2:
        route = R2(route)
    else:
        route = R3(route)
    if objective_value > objective_function(route,using_truck):
        objective_value = objective_function(route,using_truck)
        if decide_number == 1:
            first_number = first_number + 1
        elif decide_number == 2:
            second_number = second_number + 1
        else:
            third_number = third_number + 1
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone
    #print(route_possibility(route))
    iteration_number = iteration_number + 1
    if route_possibility(route) == False:
        print(iteration_number)
print(route)
print(route_possibility(route))
print("objective_value",objective_value)
print("値",(first_number,second_number,third_number))
"""

iteration_number = 0
route = copy.deepcopy(first_route)
using_truck = first_using_truck
using_drone = first_using_drone
objective_value = objective_function(route,using_truck)
n1 = []
start1 = time.perf_counter()
time_number = 0
while time_number <= 600:
#while iteration_number <= 100:
    now = time.perf_counter()
    if now - start1 > time_number:
        time_number = time_number + 60
        n1.append(objective_value)
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    #print("destroy_node",destroy_node)
    if iteration_number % 2 == 0:
        route = D1(route,3)
    else:
        route = D2(route,2)
    if iteration_number % 3 == 0:
        route = R1(route)
    elif iteration_number % 3 == 1:
        route = R3(route)
    else:
        route = R2(route)
    if objective_value > objective_function(route,using_truck):
        objective_value = objective_function(route,using_truck)
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone
    #print(route_possibility(route))
    iteration_number = iteration_number + 1
    if route_possibility(route) == False:
        print(iteration_number)
print(route)
print(route_possibility(route))
print("objective_value",objective_value)

iteration_number = 0
route = copy.deepcopy(first_route)
using_truck = first_using_truck
using_drone = first_using_drone
objective_value = objective_function(route,using_truck)
n2= []
start2 = time.perf_counter()
time_number = 0
while time_number <= 600:
    now = time.perf_counter()
    if now - start2 > time_number:
        time_number = time_number + 60
        n2.append(objective_value)
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    if iteration_number % 20 == 19:
        route = D5(route,1)
    elif iteration_number % 2 == 0:
        route = D1(route,3)
    else:
        route = D2(route,2)
    if iteration_number % 3 == 0:
        route = R1(route)
    elif iteration_number % 3 == 2:
        route = R3(route)
    else:
        route = R2(route)
    if objective_value > objective_function(route,using_truck):
        objective_value = objective_function(route,using_truck)
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone
    #print(route_possibility(route))
    iteration_number = iteration_number + 1
print(route)
print(route_possibility(route))
print("objective_value",objective_value)
"""

iteration_number = 0
route = copy.deepcopy(first_route)
using_truck = first_using_truck
using_drone = first_using_drone
objective_value = objective_function(route,using_truck)
n3 = []
start3 = time.perf_counter()
time_number = 0
while time_number <= 300:
    now = time.perf_counter()
    if now - start3 > time_number:
        time_number = time_number + 15
        n3.append(objective_value)
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    #print("destroy_node",destroy_node)
    if iteration_number % 2 == 0:
        route = D1(route,3)
    else:
        route = D2(route,2)
    if iteration_number % 4 == 0 or iteration_number % 4 == 3:
        route = R3(route)
    else:
        route = R2(route)
    if objective_value > objective_function(route,using_truck):
        objective_value = objective_function(route,using_truck)
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone

    iteration_number = iteration_number + 1
print(route)
print(route_possibility(route))
print("objective_value",objective_value)
"""
"""
iteration_number = 0
route = copy.deepcopy(first_route)
using_truck = first_using_truck
using_drone = first_using_drone
objective_value = objective_function(route,using_truck)
n4 = []
start4 = time.perf_counter()
time_number = 0
destroy1_decrease = 0
destroy2_decrease = 0
repair1_deecrease = 0
repair2_deecrease = 0
repair3_deecrease = 0
while time_number <= 300:
    now = time.perf_counter()
    if now - start4 > time_number:
        time_number = time_number + 60
        print("destroy",(destroy1_decrease,destroy2_decrease))
        print("repair",(repair1_deecrease,repair2_deecrease,repair3_deecrease))
    current_route = copy.deepcopy(route)
    current_truck = using_truck
    current_drone = using_drone
    #print("destroy_node",destroy_node)
    if iteration_number % 2 == 0:
        route = D1(route,3)
    else:
        route = D2(route,2)
    if iteration_number % 3 == 0:
        route = R1(route)
    elif iteration_number % 3 == 1:
        route = R2(route)
    else:
        route = R3(route)
    value = objective_function(route,using_truck)
    if objective_value > value:
        if iteration_number % 6 == 0:
            destroy1_decrease = destroy1_decrease + 1
            repair1_deecrease = repair1_deecrease + 1
        elif iteration_number % 6 == 1:
            destroy2_decrease = destroy2_decrease + 1
            repair2_deecrease = repair2_deecrease + 1
        elif iteration_number % 6 == 2:
            destroy1_decrease = destroy1_decrease + 1
            repair3_deecrease = repair3_deecrease + 1
        elif iteration_number % 6 == 3:
            destroy2_decrease = destroy2_decrease + 1
            repair1_deecrease = repair1_deecrease + 1
        elif iteration_number % 6 == 4:
            destroy1_decrease = destroy1_decrease + 1
            repair2_deecrease = repair2_deecrease + 1
        else:
            destroy2_decrease = destroy2_decrease + 1
            repair3_deecrease = repair3_deecrease + 1
        objective_value = value
    else:
        route = current_route
        using_truck = current_truck
        using_drone = current_drone

    iteration_number = iteration_number + 1
print(route)
print(route_possibility(route))
print("objective_value",objective_value)
print("D減少量",(destroy1_decrease,destroy2_decrease))
print("D減少回数",(first_destroy,second_destroy))
print("R減少量",(repair1_deecrease,repair2_deecrease,repair3_deecrease))

print("R減少量",(first_repair,second_repair,third_repair))
"""



#print(end2-start2)
#print(route)

#(objective_route,value) = R1(route,destroy_node)

#print("objedctive_value:",objective_value)
#print("Truck_route", route)
#print("using_drone",using_drone)

"""
node = []
for i in range(1,101):
    node.append(i)
for i in range(0,len(route)):
    for j in range(0,len(route[i])):
        if route[i][j] in node:
            node.remove(route[i][j])
print("node:",node)
#print("using_truck:",using_truck)
"""

end = time.perf_counter()
"""
fig, ax = plt.subplots()
ax.plot(A,n1,label = R1)
ax.plot(A,n2,label = R2)
ax.plot(A,n3,label = R3)
ax.plot(A,n4,label = (R1,R2,R3))
ax.legend(loc='upper right')
plt.show()
"""
fig, ax = plt.subplots()
ax.plot(A,n1,label = "(D1,D2)")
ax.plot(A,n2,label = "(D1,D2,D4)")
#ax.plot(A,n3,label = (R2,R3))
#ax.plot(A,n4,label = (R1,R2))
#ax.plot(A,n5,label = (R2,R3))
#ax.plot(A,n6,label = (R2,R3))
#ax.plot(A,n7,label = (R1,R2,R3))
ax.legend(loc='upper right')
plt.show()
"""
fig, ax = plt.subplots()
ax.plot(A,n1,label = R22)
ax.plot(A,n2,label = R2)
ax.legend(loc='upper right')
plt.show()
"""
#print("time:",end-start)
#visualize(route)
