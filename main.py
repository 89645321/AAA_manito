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
new_connections_0 = {}
new_connections_1 = {}
new_connections_2 = {}

# input json
autoconnectInput = open("autoconnectInputExample.json")
json_object = json.load(autoconnectInput)

for user in json_object["users"]:
    student_id = int(user.get("col_no"))
    # student_id <= n에서 n은 올해 신입생 학번 이상 100 미만이어야 함
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
            _followee = -1
            _follower = -1
            if user.user_id in connections[i * 2].keys():
                _followee = connections[i * 2][user.user_id]
                connections[i * 2].pop(user.user_id)
            if user.user_id in connections[i * 2 + 1].keys():
                _follower = connections[i * 2 + 1][user.user_id]
                connections[i * 2 + 1].pop(user.user_id)
            if _follower in connections[i * 2].keys():
                connections[i * 2].pop(_follower)
            if _followee in connections[i * 2 + 1].keys():
                connections[i * 2 + 1].pop(_followee)


# 각종 함수
def random_assign(temp, new_connection, cmd, follower_random, followee_random):
    # 학번별로 ob, yb 배정
    temp = sorted(temp, key=lambda user: user.col_no)

    middle = len(temp) // 2
    ob_flag = True
    if cmd:
        if (len(temp) % 2) == 1 and temp.index(follower_random) <= middle:
            middle += 1
        if temp.index(follower_random) < middle:
            ob_flag = False

    ob = temp[:middle]
    yb = temp[middle:]

    # 마니또 배정
    if cmd:
        if ob_flag:
            yb.remove(follower_random)
        else:
            ob.remove(follower_random)
        follower = follower_random
        last_followee = followee_random
    else:
        follower = random.choice(yb)
        yb.remove(follower)
        last_followee = follower

    for i in range(len(ob) + len(yb)):
        if ob_flag:
            followee = random.choice(ob)
            ob.remove(followee)
        else:
            followee = random.choice(yb)
            yb.remove(followee)
        new_connection[follower.user_id] = followee.user_id
        follower = followee
        ob_flag = not ob_flag

    if command == "0":
        new_connection[follower.user_id] = last_followee.user_id

    return new_connection


def assign(follower_not_assigned, followee_not_assigned, all_not_assigned, new_connection):
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
            new_connection[follower.user_id] = follower_not_assigned[i].user_id

        # 마니또 배정
        temp = all_not_assigned.copy()
        temp.append(follower_random)
        new_connection = random_assign(temp, new_connection, True, follower_random, followee_random)

    # 반쪽 미배정인 사람들이 없는 경우
    else:
        # 배정이 필요하지 않은 경우
        if len(all_not_assigned) == 0:
            pass
        # 한 명만 미배정인 경우
        elif len(all_not_assigned) == 1 and day < 2:
            # 선 배정이면 아무것도 안 함
            # 원 배정 중 기존 사이클을 끊고 배정이 가능한 경우
            if command == "0" and not (len(users) == 1 or users[1].exit_at < 3):
                for user in users:
                    if user.user_id != all_not_assigned[0].user_id:
                        follower = user.user_id
                        followee = connections[4][follower]
                        connections[4].pop(follower)
                        connections[5].pop(followee)
                        new_connection[follower] = all_not_assigned[0].user_id
                        new_connection[all_not_assigned[0].user_id] = followee
                        break
        # 그 외 일반적인 경우
        else:
            new_connection = random_assign(all_not_assigned, new_connection, False, -1, -1)

    return new_connection


def divide1(follower_not_assigned, followee_not_assigned, all_not_assigned, j, _user):
    if _user.user_id not in connections[j * 2].keys() and _user.user_id not in connections[j * 2].keys():
        all_not_assigned.append(_user)
    elif _user.user_id not in connections[j * 2 + 1].keys():
        follower_not_assigned.append(_user)
    elif _user.user_id not in connections[j * 2].keys():
        followee_not_assigned.append(_user)
    return follower_not_assigned, followee_not_assigned, all_not_assigned


def divide2(follower1, followee1, all1, follower2, followee2, all2, j, _user):
    if _user.user_id not in connections[j].keys() and _user.user_id not in connections[j + 1].keys():
        if _user.user_id not in connections[j + 2].keys() and _user.user_id not in connections[j + 3].keys():
            all2.append(_user)
        else:
            all1.append(_user)
    elif _user.user_id not in connections[j + 1].keys():
        if _user.user_id not in connections[j + 3].keys() and _user.user_id in connections[j + 2].keys() and \
                connections[j + 2][_user.user_id] == connections[j][_user.user_id]:
            follower2.append(_user)
        else:
            follower1.append(_user)
    elif _user.user_id not in connections[j].keys():
        if _user.user_id not in connections[j + 2].keys() and _user.user_id in connections[j + 3].keys() and \
                connections[j + 3][_user.user_id] == connections[j + 1][_user.user_id]:
            followee2.append(_user)
        else:
            followee1.append(_user)
    return follower1, followee1, all1, follower2, followee2, all2


# 2. 참가자 분류
# 3. 배정
# 1일차일 때


if day == 0:
    # 2. 참가자 분류
    followee_not_assigned_0_1 = []
    follower_not_assigned_0_1 = []
    all_not_assigned_0_1 = []

    followee_not_assigned_0_2 = []
    follower_not_assigned_0_2 = []
    all_not_assigned_0_2 = []

    followee_not_assigned_0_3 = []
    follower_not_assigned_0_3 = []
    all_not_assigned_0_3 = []

    for user in users:
        if user.exit_at < 1:
            break

        elif user.exit_at == 1:
            divide1(follower_not_assigned_0_1, followee_not_assigned_0_1, all_not_assigned_0_1, 0, user)

        elif user.exit_at == 2:
            follower_not_assigned_0_1, followee_not_assigned_0_1, all_not_assigned_0_1, \
                follower_not_assigned_0_2, followee_not_assigned_0_2, all_not_assigned_0_2 \
                = divide2(follower_not_assigned_0_1, followee_not_assigned_0_1, all_not_assigned_0_1,
                          follower_not_assigned_0_2, followee_not_assigned_0_2, all_not_assigned_0_2, 0, user)

        else:
            if user.user_id not in connections[0].keys() and user.user_id not in connections[1].keys():
                if user.user_id not in connections[2].keys() and user.user_id not in connections[3].keys():
                    if user.user_id not in connections[4].keys() and user.user_id not in connections[5].keys():
                        all_not_assigned_0_3.append(user)
                    else:
                        all_not_assigned_0_2.append(user)
                else:
                    all_not_assigned_0_1.append(user)

            elif user.user_id not in connections[1].keys():
                if user.user_id not in connections[3].keys() and user.user_id in connections[2].keys() and \
                        connections[2][user.user_id] == connections[0][user.user_id]:
                    if user.user_id not in connections[5].keys() and user.user_id in connections[4].keys() and \
                            connections[4][user.user_id] == connections[0][user.user_id]:
                        follower_not_assigned_0_3.append(user)
                    else:
                        follower_not_assigned_0_2.append(user)
                else:
                    follower_not_assigned_0_1.append(user)

            elif user.user_id not in connections[0].keys():
                if user.user_id not in connections[2].keys() and user.user_id in connections[3].keys() and \
                        connections[3][user.user_id] == connections[1][user.user_id]:
                    if user.user_id not in connections[4].keys() and user.user_id in connections[5].keys() and \
                            connections[5][user.user_id] == connections[1][user.user_id]:
                        followee_not_assigned_0_3.append(user)
                    else:
                        followee_not_assigned_0_2.append(user)
                else:
                    followee_not_assigned_0_1.append(user)

    # 3. 배정
    # 선 배정
    if command == "1":
        new_connections_0 = assign(follower_not_assigned_0_1, followee_not_assigned_0_1, all_not_assigned_0_1, {})
        new_connections_1 = assign(follower_not_assigned_0_2, followee_not_assigned_0_2, all_not_assigned_0_2, {})
        new_connections_2 = assign(follower_not_assigned_0_3, followee_not_assigned_0_3, all_not_assigned_0_3, {})
        new_connections_0.update(new_connections_1)
        new_connections_0.update(new_connections_2)
        new_connections_1.update(new_connections_2)
    # 원 배정
    else:
        if len(follower_not_assigned_0_1) == 0 and len(followee_not_assigned_0_1) == 0 and len(all_not_assigned_0_1) == 1:
            if len(follower_not_assigned_0_2) == 0 and len(followee_not_assigned_0_2) == 0 and len(all_not_assigned_0_2) == 1:
        # 1-2 미배정 인원 1명, 1-3 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_not_assigned_0_3) == 0 and len(followee_not_assigned_0_3) == 0 and len(all_not_assigned_0_3) == 1:
                    new_connections_0[all_not_assigned_0_1[0].user_id] = all_not_assigned_0_2[0].user_id
                    new_connections_0[all_not_assigned_0_2[0].user_id] = all_not_assigned_0_3[0].user_id
                    new_connections_0[all_not_assigned_0_3[0].user_id] = all_not_assigned_0_1[0].user_id
        # 1-2 미배정 인원 1명, 1-3 미배정 인원 1명
                else:
                    new_connections_0[all_not_assigned_0_1[0].user_id] = all_not_assigned_0_2[0].user_id
                    new_connections_0[all_not_assigned_0_2[0].user_id] = all_not_assigned_0_1[0].user_id
                    new_connections_2 = assign(follower_not_assigned_0_3, followee_not_assigned_0_3, all_not_assigned_0_3, {})
                    new_connections_0.update(new_connections_2)
                    new_connections_1 = new_connections_0.copy()
            else:
        # 1-2 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_not_assigned_0_3) == 0 and len(followee_not_assigned_0_3) == 0 and len(all_not_assigned_0_3) == 1:
                    new_connections_0[all_not_assigned_0_1[0].user_id] = all_not_assigned_0_3[0].user_id
                    new_connections_0[all_not_assigned_0_3[0].user_id] = all_not_assigned_0_1[0].user_id
                    new_connections_1 = assign(follower_not_assigned_0_2, followee_not_assigned_0_2, all_not_assigned_0_2, {})
                    new_connections_0.update(new_connections_1)
        # 1-2 미배정 인원 1명
                else:
                    user = all_not_assigned_0_1[0]
                    # 1-3 먼저 배정
                    new_connections_0 = assign(follower_not_assigned_0_2, followee_not_assigned_0_2, all_not_assigned_0_2, {})
                    new_connections_1 = new_connections_0.copy()
                    # 1-3 새 배정이 없을 때
                    if len(new_connections_1.keys()) == 0:
                        # 1-4 배정
                        new_connections_2 = assign(follower_not_assigned_0_3, followee_not_assigned_0_3, all_not_assigned_0_3, {})
                        new_connections_0.update(new_connections_2)
                        new_connections_1.update(new_connections_2)
                        # 1-4 새 배정이 없을 때
                        if len(new_connections_2.keys()) == 0:
                            # 1-2 나머지 인원 아예 없는지 확인
                            no_assignment = True
                            for u in users:
                                if u.enter_at <= 0 and u.exit_at >= 2 and u.user_id != user.user_id:
                                    no_assignment = False
                                    break
                            # 인원이 있다면 배정 중 아무데나 끼운다
                            if not no_assignment:
                                random.shuffle(users)
                                for u in users:
                                    if u.enter_at <= 0 and u.exit_at >= 2 and u.user_id != user.user_id:
                                        followee = connections[1][u.user_id]
                                        connections[0].pop(u.user_id)
                                        connections[1].pop(followee)
                                        new_connections_0[u.user_id] = user.user_id
                                        new_connections_0[user.user_id] = followee
                                        break
                        # 1-4 새 배정이 있을 때
                        else:
                            follower = random.choice(new_connections_2.keys())
                            followee = new_connections_2[follower]
                            new_connections_0[follower] = user.user_id
                            new_connections_0[user.user_id] = followee
                    # 1-3 새 배정이 있을 때
                    else:
                        # 끼워넣기
                        follower = random.choice(new_connections_0.keys())
                        followee = new_connections_0[follower]
                        new_connections_0[follower] = user.user_id
                        new_connections_0[user.user_id] = followee
                        # 1-4 배정
                        new_connections_2 = assign(follower_not_assigned_0_3, followee_not_assigned_0_3, all_not_assigned_0_3, {})
                        new_connections_0.update(new_connections_2)
                        new_connections_1.update(new_connections_2)
        else:
            if len(follower_not_assigned_0_2) == 0 and len(followee_not_assigned_0_2) == 0 and len(all_not_assigned_0_2) == 1:
        # 1-3 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_not_assigned_0_3) == 0 and len(followee_not_assigned_0_3) == 0 and len(all_not_assigned_0_3) == 1:
                    pass
        # 1-3 미배정 인원 1명
                else:
                    pass
            else:
        # 1-4 미배정 인원 1명
                if len(follower_not_assigned_0_3) == 0 and len(followee_not_assigned_0_3) == 0 and len(all_not_assigned_0_3) == 1:
                    pass
        # 그 외 일반적인 경우
                else:
                    pass
# 2일차일 때
elif day == 1:
    # 2. 참가자 분류
    followee_not_assigned_1_3 = []
    follower_not_assigned_1_3 = []
    all_not_assigned_1_3 = []

    followee_not_assigned_1_2 = []
    follower_not_assigned_1_2 = []
    all_not_assigned_1_2 = []

    for user in users:
        if user.exit_at < 2:
            break
        elif user.exit_at == 2:
            divide1(follower_not_assigned_1_2, followee_not_assigned_1_2, all_not_assigned_1_2, 1, user)
        else:
            follower_not_assigned_1_2, followee_not_assigned_1_2, all_not_assigned_1_2, \
                follower_not_assigned_1_3, followee_not_assigned_1_3, all_not_assigned_1_3 \
                = divide2(follower_not_assigned_1_2, followee_not_assigned_1_2, all_not_assigned_1_2,
                          follower_not_assigned_1_3, followee_not_assigned_1_3, all_not_assigned_1_3, 2, user)

    # 3. 배정
    # 선 배정
    if command == "1":
        new_connections_1 = assign(follower_not_assigned_1_2, followee_not_assigned_1_2, all_not_assigned_1_2, {})
        new_connections_2 = assign(follower_not_assigned_1_3, followee_not_assigned_1_3, all_not_assigned_1_3, {})
        new_connections_1.update(new_connections_2)
    # 원 배정
    else:
        # 2-3 미배정 인원 1명, 2-4 미배정 인원 1명일 때
        if len(follower_not_assigned_1_2) == 0 and len(followee_not_assigned_1_2) == 0 and len(all_not_assigned_1_2) == 1:
            if len(follower_not_assigned_1_3) == 0 and len(followee_not_assigned_1_3) == 0 and len(all_not_assigned_1_3) == 1:
                new_connections_1[all_not_assigned_1_2[0].user_id] = all_not_assigned_1_3[0].user_id
                new_connections_1[all_not_assigned_1_3[0].user_id] = all_not_assigned_1_2[0].user_id
            # 2-3 미배정 인원만 1명일 때
            else:
                user = all_not_assigned_1_2[0]
                # 2-4 먼저 배정
                new_connections_1 = assign(follower_not_assigned_1_3, followee_not_assigned_1_3, all_not_assigned_1_3, {})
                new_connections_2 = new_connections_1.copy()
                # 2-4 새 배정이 없을 때
                if len(new_connections_2.keys()) == 0:
                    # 2-3 나머지 인원 아예 없는지 확인
                    no_assignment = True
                    for u in users:
                        if u.enter_at <= 1 and u.exit_at >= 2 and u.user_id != user.user_id:
                            no_assignment = False
                            break
                    # 인원이 있다면 배정 중 아무데나 끼운다
                    if not no_assignment:
                        random.shuffle(users)
                        for u in users:
                            if u.enter_at <= 1 and u.exit_at >= 2 and u.user_id != user.user_id:
                                followee = connections[2][u.user_id]
                                connections[2].pop(u.user_id)
                                connections[3].pop(followee)
                                new_connections_1[u.user_id] = user.user_id
                                new_connections_1[user.user_id] = followee
                                break
                #2-4 새 배정이 있을 때
                else:
                    follower = random.choice(new_connections_1.keys())
                    followee = new_connections_1[follower]
                    new_connections_1[follower] = user.user_id
                    new_connections_1[user.user_id] = followee
        # 2-4 미배정 인원만 1명일 때
        else:
            user = all_not_assigned_1_3[0]
            # 2-3 먼저 배정
            new_connections_1 = assign(follower_not_assigned_1_3, followee_not_assigned_1_3, all_not_assigned_1_3, {})
            # 2-3 새 배정이 없을 때
            if len(new_connections_1.keys()) == 0:
                # 2-3 나머지 인원 아예 없는지 확인
                no_assignment = True
                for u in users:
                    if u.enter_at <= 1 and u.exit_at >= 2 and u.user_id != user.user_id:
                        no_assignment = False
                        break
                # 인원이 있다면 배정 중 아무데나 끼운다
                if not no_assignment:
                    random.shuffle(users)
                    for u in users:
                        if u.enter_at <= 1 and u.exit_at >= 2 and u.user_id != user.user_id:
                            followee = connections[2][u.user_id]
                            connections[2].pop(u.user_id)
                            connections[3].pop(followee)
                            new_connections_1[u.user_id] = user.user_id
                            new_connections_1[user.user_id] = followee
                            break
            # 2-3 새 배정이 있을 때
            else:
                follower = random.choice(list(new_connections_1.keys()))
                followee = new_connections_1[follower]
                new_connections_1[follower] = user.user_id
                new_connections_1[user.user_id] = followee

# 3일차일 때
else:
    # 2. 참가자 분류
    followee_not_assigned_2_3 = []
    follower_not_assigned_2_3 = []
    all_not_assigned_2_3 = []
    for user in users:
        if user.exit_at < 3:
            break
        follower_not_assigned_2_3, followee_not_assigned_2_3, all_not_assigned_2_3 = divide1(
            follower_not_assigned_2_3, followee_not_assigned_2_3, all_not_assigned_2_3, 2, user)

    # 3. 배정
    new_connections_2 = assign(follower_not_assigned_2_3, followee_not_assigned_2_3, all_not_assigned_2_3, {})

for connection in new_connections_1:
    print("1")
    print(connection, new_connections_1[connection])

for connection in new_connections_2:
    print("2")
    print(connection, new_connections_2[connection])
