import json
import random
import sys


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
autoconnectInput = sys.stdin#open("autoconnectInput.json")
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
            followee_del = -1
            follower_del = -1
            if user.user_id in connections[i * 2].keys():
                followee_del = connections[i * 2][user.user_id]
                connections[i * 2].pop(user.user_id)
            if user.user_id in connections[i * 2 + 1].keys():
                follower_del = connections[i * 2 + 1][user.user_id]
                connections[i * 2 + 1].pop(user.user_id)
            if follower_del in connections[i * 2].keys():
                connections[i * 2].pop(follower_del)
            if followee_del in connections[i * 2 + 1].keys():
                connections[i * 2 + 1].pop(followee_del)

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


def assign(follower, followee, all, new_connection):
    # 반쪽 미배정인 사람들이 있는 경우
    if len(followee) > 0:
        # follower, followee만 없는 사람들 중 한 쌍 골라서 빼기
        follower_random = random.choice(followee)
        followee_random = random.choice(follower)
        followee.remove(follower_random)
        follower.remove(followee_random)

        # follower, followee만 없는 사람들 짝지어주기(위에서 뺀 한 쌍 빼고)
        for i in range(len(followee)):
            follower_rand = random.choice(followee)
            followee.remove(follower_rand)
            new_connection[follower_rand.user_id] = follower[i].user_id

        # 마니또 배정
        temp = all.copy()
        temp.append(follower_random)
        new_connection = random_assign(temp, new_connection, True, follower_random, followee_random)

    # 반쪽 미배정인 사람들이 없는 경우
    else:
        # 배정이 필요하지 않은 경우, 한 명만 미배정인 경우
        if len(all) <= 1:
            pass
        # 그 외 일반적인 경우
        else:
            new_connection = random_assign(all, new_connection, False, -1, -1)

    return new_connection


def divide1(follower, followee, all, j, _user):
    if _user.user_id not in connections[j].keys() and _user.user_id not in connections[j + 1].keys():
        all.append(_user)
    elif _user.user_id not in connections[j + 1].keys():
        follower.append(_user)
    elif _user.user_id not in connections[j].keys():
        followee.append(_user)
    return follower, followee, all


def divide2(follower1, followee1, all1, follower2, followee2, all2, j):
    for fwer in follower1:
        if fwer.user_id in connections[j].keys():
            fwee = connections[j][fwer.user_id]
            while True:
                if fwee in connections[j].keys():
                    fwee = connections[j][fwee]
                else:
                    for u in users:
                        if u.user_id == fwee:
                            fwee = u
                            break
                    if fwee in followee1:
                        follower2.append(fwer)
                        followee2.append(fwee)
                    break

    for fwer in follower2:
        if fwer in follower1:
            follower1.remove(fwer)

    for fwee in followee2:
        if fwee in followee1:
            followee1.remove(fwee)

    for u in all1:
        if u.user_id not in connections[j].keys() and u.user_id not in connections[j+1].keys():
            all2.append(u)

    for u in all2:
        if u in all1:
            all1.remove(u)

    return follower1, followee1, all1, follower2, followee2, all2


# 2. 참가자 분류
# 3. 배정
# 1일차일 때
if day == 0:
    # 2. 참가자 분류
    followee_0_1 = []
    follower_0_1 = []
    all_0_1 = []

    followee_0_2 = []
    follower_0_2 = []
    all_0_2 = []

    followee_0_3 = []
    follower_0_3 = []
    all_0_3 = []

    for user in users:
        if user.exit_at < 1:
            break
        else:
            follower_0_1, followee_0_1, all_0_1 = divide1(follower_0_1, followee_0_1, all_0_1, 0, user)

    follower_0_1, followee_0_1, all_0_1, follower_0_2, followee_0_2, all_0_2 = divide2(follower_0_1, followee_0_1, all_0_1, follower_0_2, followee_0_2, all_0_2, 2)
    follower_0_2, followee_0_2, all_0_2, follower_0_3, followee_0_3, all_0_3 = divide2(follower_0_2, followee_0_2, all_0_2, follower_0_3, followee_0_3, all_0_3, 4)

    # 3. 배정
    # 선 배정
    if command == "1":
        new_connections_0 = assign(follower_0_1, followee_0_1, all_0_1, {})
        new_connections_1 = assign(follower_0_2, followee_0_2, all_0_2, {})
        new_connections_2 = assign(follower_0_3, followee_0_3, all_0_3, {})
        new_connections_0.update(new_connections_1)
        new_connections_0.update(new_connections_2)
        new_connections_1.update(new_connections_2)
    # 원 배정
    else:
        if len(follower_0_1) == 0 and len(all_0_1) == 1:
            if len(follower_0_2) == 0 and len(all_0_2) == 1:
                # 1-2 미배정 인원 1명, 1-3 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_0_3) == 0 and len(followee_0_3) == 0 and len(
                        all_0_3) == 1:
                    new_connections_0[all_0_1[0].user_id] = all_0_2[0].user_id
                    new_connections_0[all_0_2[0].user_id] = all_0_3[0].user_id
                    new_connections_0[all_0_3[0].user_id] = all_0_1[0].user_id
                # 1-2 미배정 인원 1명, 1-3 미배정 인원 1명
                else:
                    new_connections_0[all_0_1[0].user_id] = all_0_2[0].user_id
                    new_connections_0[all_0_2[0].user_id] = all_0_1[0].user_id
                    new_connections_2 = assign(follower_0_3, followee_0_3, all_0_3, {})
                    new_connections_0.update(new_connections_2)
                    new_connections_1 = new_connections_2.copy()
            else:
                # 1-2 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_0_3) == 0 and len(all_0_3) == 1:
                    new_connections_0[all_0_1[0].user_id] = all_0_3[0].user_id
                    new_connections_0[all_0_3[0].user_id] = all_0_1[0].user_id
                    new_connections_1 = assign(follower_0_2, followee_0_2, all_0_2, {})
                    new_connections_0.update(new_connections_1)
                # 1-2 미배정 인원 1명
                # 이 경우 1-2 미배정 인원은 마짱이 배정해줘야 함
                else:
                    new_connections_2 = assign(follower_0_3, followee_0_3, all_0_3, {})
                    new_connections_1 = assign(follower_0_2, followee_0_2, all_0_2, {})
                    new_connections_0.update(new_connections_1)
                    new_connections_0.update(new_connections_2)
                    new_connections_1.update(new_connections_2)
        else:
            if len(follower_0_2) == 0 and len(all_0_2) == 1:
                # 1-3 미배정 인원 1명, 1-4 미배정 인원 1명
                if len(follower_0_3) == 0 and len(all_0_3) == 1:
                    new_connections_1[all_0_2[0].user_id] = all_0_3[0].user_id
                    new_connections_1[all_0_3[0].user_id] = all_0_2[0].user_id
                    new_connections_0 = assign(follower_0_1, followee_0_1, all_0_1, {})
                    new_connections_0.update(new_connections_1)
                # 1-3 미배정 인원 1명
                # 이 경우 1-3 미배정 인원은 마짱이 배정해줘야 함
                else:
                    new_connections_0 = assign(follower_0_1, followee_0_1, all_0_1, {})
                    new_connections_2 = assign(follower_0_3, followee_0_3, all_0_3, {})
                    new_connections_0.update(new_connections_2)
                    new_connections_1 = new_connections_2.copy()
            else:
                # 1-4 미배정 인원 1명
                # 이 경우 1-4 미배정 인원은 마짱이 배정해줘야 함
                if len(follower_0_3) == 0 and len(all_0_3) == 1:
                    new_connections_0 = assign(follower_0_1, followee_0_1, all_0_1, {})
                    new_connections_1 = assign(follower_0_2, followee_0_2, all_0_2, {})
                    new_connections_0.update(new_connections_1)
                # 그 외 일반적인 경우
                else:
                    new_connections_0 = assign(follower_0_1, followee_0_1, all_0_1, {})
                    new_connections_1 = assign(follower_0_2, followee_0_2, all_0_2, {})
                    new_connections_2 = assign(follower_0_3, followee_0_3, all_0_3, {})
                    new_connections_0.update(new_connections_1)
                    new_connections_0.update(new_connections_2)
                    new_connections_1.update(new_connections_2)
# 2일차일 때
elif day == 1:
    # 2. 참가자 분류
    followee_1_3 = []
    follower_1_3 = []
    all_1_3 = []

    followee_1_2 = []
    follower_1_2 = []
    all_1_2 = []

    for user in users:
        if user.exit_at < 2:
            break
        else:
            follower_1_2, followee_1_2, all_1_2 = divide1(follower_1_2, followee_1_2, all_1_2, 2, user)

    follower_1_2, followee_1_2, all_1_2, follower_1_3, followee_1_3, all_1_3 = divide2(follower_1_2, followee_1_2, all_1_2, follower_1_3, followee_1_3, all_1_3, 4)

    # 3. 배정
    # 선 배정
    if command == "1":
        new_connections_1 = assign(follower_1_2, followee_1_2, all_1_2, {})
        new_connections_2 = assign(follower_1_3, followee_1_3, all_1_3, {})
        new_connections_1.update(new_connections_2)
    # 원 배정
    else:
        if len(follower_1_2) == 0 and len(all_1_2) == 1:
        # 2-3, 2-4 미배정 인원 1명일 때
            if len(follower_1_3) == 0 and len(all_1_3) == 1:
                new_connections_1[all_1_2[0].user_id] = all_1_3[0].user_id
                new_connections_1[all_1_3[0].user_id] = all_1_2[0].user_id
        # 2-3 미배정 인원만 1명일 때
        # 이 경우 2-3 미배정 인원은 마짱이 배정해줘야 함
            else:
                new_connections_1 = assign(follower_1_3, followee_1_3, all_1_3, {})
                new_connections_2 = new_connections_1.copy()
        else:
        # 2-4 미배정 인원만 1명일 때
        # 이 경우 2-4 미배정 인원은 마짱이 배정해줘야 함
            if len(follower_1_3) == 0 and len(all_1_3) == 1:
                new_connections_1 = assign(follower_1_2, followee_1_2, all_1_2, {})
        # 그 외 일반적인 경우
            else:
                new_connections_1 = assign(follower_1_2, followee_1_2, all_1_2, {})
                new_connections_2 = assign(follower_1_3, followee_1_3, all_1_3, {})
                new_connections_1.update(new_connections_2)

# 3일차일 때
else:
    # 2. 참가자 분류
    followee_2_3 = []
    follower_2_3 = []
    all_2_3 = []
    for user in users:
        if user.exit_at < 3:
            break
        follower_2_3, followee_2_3, all_2_3 = divide1(follower_2_3, followee_2_3, all_2_3, 4, user)

    # 3. 배정
    new_connections_2 = assign(follower_2_3, followee_2_3, all_2_3, {})

connections[0].update(new_connections_0)
connections[2].update(new_connections_1)
connections[4].update(new_connections_2)

# output json
out1 = ""
for key in connections[0].keys():
    out1 += "\t\t{\n\t\t\t\"follower_id\": " + str(key) + ", \n\t\t\t\"followee_id\": " + str(connections[0][key]) + "\n\t\t},\n"
out1 = out1[:-2]
out1 = "{\n\t\"connections0\":[\n" + out1 + "\n\t],"
out2 = ""
for key in connections[2].keys():
    out2 += "\t\t{\n\t\t\t\"follower_id\": " + str(key) + ", \n\t\t\t\"followee_id\": " + str(connections[2][key]) + "\n\t\t},\n"
out2 = out2[:-2]
out2 = "\n\t\"connections1\":[\n" + out2 + "\n\t],"
out3 = ""
for key in connections[4].keys():
    out3 += "\t\t{\n\t\t\t\"follower_id\": " + str(key) + ", \n\t\t\t\"followee_id\": " + str(connections[4][key]) + "\n\t\t},\n"
out3 = out3[:-2]
out3 = "\n\t\"connections2\":[\n" + out3 + "\n\t]\n}"
json_out = out1 + out2 + out3

f = sys.stdout
f.write(json_out)
f.close()
