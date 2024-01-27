import json
import random


class User:
    def __init__(self, user_id, col_no, enter_at, exit_at):
        self.user_id = user_id
        self.col_no = col_no
        self.enter_at = enter_at
        self.exit_at = exit_at


last_day = 3
users = []
# 0: 0, 1: 0 reverse, 2: 1, 3: 1 reverse, 4: 2, 5: 2 reverse
connections = [{}, {}, {}, {}, {}, {}]

# input json
autoconnectInput = open("autoconnectInputExample.json")
json_object = json.load(autoconnectInput)

for user in json_object["users"]:
    student_id = int(user.get("col_no"))
    # 년도가 바뀌면 업데이트해야 함
    if student_id <= 60:
        student_id += 100
    users.append(
        User(
            user.get("user_id"),
            student_id,
            user.get("schedule").get("enter_at").get("major"),
            user.get("schedule").get("exit_at").get("major")
        )
    )

for connection in json_object["connections0"]:
    connections[0][connection.get("follower_id")] = connection.get("followee_id")
    connections[1][connection.get("followee_id")] = connection.get("follower_id")

for connection in json_object["connections1"]:
    connections[2][connection.get("follower_id")] = connection.get("followee_id")
    connections[3][connection.get("followee_id")] = connection.get("follower_id")

for connection in json_object["connections2"]:
    connections[4][connection.get("follower_id")] = connection.get("followee_id")
    connections[5][connection.get("followee_id")] = connection.get("follower_id")

command = json_object["command"]
day = json_object["day"]

# 1. 참가자가 가는 날짜를 앞당긴 경우 connection 삭제
random.shuffle(users)
users = sorted(users, key=lambda user: user.exit_at, reverse=True)
for i in range(day, last_day):
    for user in users:
        if user.exit_at <= i:
            followee = -1
            follower = -1
            if user.user_id in connections[i*2].keys():
                followee = connections[i*2][user.user_id]
            if user.user_id in connections[i*2+1].keys():
                follower = connections[i*2+1][user.user_id]
            if user.user_id in connections[i*2].keys():
                connections[i*2].pop(user.user_id)
            if user.user_id in connections[i*2+1].keys():
                connections[i*2+1].pop(user.user_id)
            if follower in connections[i*2].keys():
                connections[i*2].pop(follower)
            if followee in connections[i*2+1].keys():
                connections[i*2+1].pop(followee)


def random_assign(OB, YB, OB_flag, new_connection, follower_assign, cmd, last_followee):
    for i in range(len(OB) + len(YB)):
        if OB_flag:
            followee_assign = random.choice(ob)
            ob.remove(followee_assign)
        else:
            followee_assign = random.choice(yb)
            yb.remove(followee_assign)
        new_connection[follower_assign.user_id] = followee_assign.user_id
        follower_assign = followee_assign
        OB_flag = not OB_flag

    if cmd == "0":
        new_connection[follower_assign.user_id] = last_followee.user_id

    return new_connection

# 2. 참가자 분류
# 3. 배정
# 1일차일 때
if day == 0:
    pass
    # 2. 참가자 분류
    # 3. 배정
# 2일차일 때
elif day == 1:
    pass
    # 2. 참가자 분류
    # 3. 배정
# 3일차일 때
else:
    # 2. 참가자 분류
    followee_not_assigned = []
    follower_not_assigned = []
    all_not_assigned = []
    for user in users:
        if user.exit_at < 3:
            break
        if user.user_id not in connections[4].keys() and user.user_id not in connections[5].keys():
            all_not_assigned.append(user)
        elif user.user_id not in connections[5].keys():
            follower_not_assigned.append(user)
        elif user.user_id not in connections[4].keys():
            followee_not_assigned.append(user)

    # 3. 배정
    new_connections = {}

    # 반쪽 미배정인 사람들이 있는 경우
    if len(followee_not_assigned) > 0:
        # follower, followee만 없는 사람들 중 한 쌍 골라서 빼기
        follower_random = random.choice(followee_not_assigned)
        followee_random = random.choice(follower_not_assigned)
        followee_not_assigned.remove(follower_random)
        follower_not_assigned.remove(followee_random)

        # follower, followee만 없는 사람들 짝지어주기(위에서 뺀 한 쌍 빼고)
        for i in range(len(followee_not_assigned)):
            follower = random.choice(followee_not_assigned)
            followee_not_assigned.remove(follower)
            new_connections[follower.user_id] = follower_not_assigned[i].user_id

        # 학번별로 ob, yb 배정
        temp = all_not_assigned.copy()
        temp.append(follower_random)
        temp = sorted(temp, key=lambda user: user.col_no)

        middle = len(temp) // 2
        ob_flag = True
        if (len(temp) % 2) == 1 and temp.index(follower_random) <= middle:
            middle += 1
        if temp.index(follower_random) < middle:
            ob_flag = False
        ob = temp[:middle]
        yb = temp[middle:]

        # line 만들기
        if ob_flag:
            yb.remove(follower_random)
        else:
            ob.remove(follower_random)
        follower = follower_random

        new_connections = random_assign(ob, yb, ob_flag, new_connections, follower, command, followee_random)

    # 반쪽 미배정인 사람들이 없는 경우
    else:
        # 배정이 필요하지 않은 경우
        if len(all_not_assigned) == 0:
            pass
        # 한 명만 미배정인 경우
        elif len(all_not_assigned) == 1:
            # 선 배정이면 아무것도 안 함
            # 원 배정 중 기존 사이클을 끊고 배정해줄 수 있는 사람이 있는 경우
            if command == "0" and not (len(users) == 1 or users[1].exit_at < 3):
                for user in users:
                    if user.user_id != all_not_assigned[0].user_id:
                        follower = user.user_id
                        followee = connections[4][follower]
                        new_connections[follower] = all_not_assigned[0].user_id
                        new_connections[all_not_assigned[0].user_id] = followee
                        break
        # 그 외 일반적인 경우
        else:
            # 학번별로 ob, yb 배정
            all_not_assigned = sorted(all_not_assigned, key=lambda user: user.col_no)

            middle = len(all_not_assigned) // 2
            ob_flag = True
            ob = all_not_assigned[:middle]
            yb = all_not_assigned[middle:]

            # cycle 만들기
            follower = random.choice(yb)
            yb.remove(follower)

            new_connections = random_assign(ob, yb, ob_flag, new_connections, follower, command, follower)

for connection in new_connections:
    print(connection, new_connections[connection])
