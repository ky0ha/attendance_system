from tkinter import *
import tkinter.font as font
import tkinter.ttk as ttk
from tkinter.messagebox import askyesno, showinfo

import os, sys, time, requests

def submit_sql(command: str, mode='get'):
    """向服务器的 api 提交一个请求，支持 get 和 post 请求，get 用于从服务器的数据库中查询某些数据
    post 用于提交对服务器数据的修改请求"""
    if mode=='get':
        r = requests.get("http://ky0ha.com:24337/api/mysql/sender?command=" + command)
    elif mode=='post':
        r = requests.post("http://ky0ha.com:24337/api/mysql/sender?command=" + command)
    return r.json()['result']

def is_leap_year(year: int):
    return (year%4==0 and (year%100!=0 or year%400==0))

class MY_GUI:
    def __init__(self, init_window_name):
        self.window_name = init_window_name
        self.init()
    
    def init(self):
        self.window_name.title("签到系统")
        self.window_name.geometry("1024x768+100+100")
        
        self.main_label = Label(self.window_name, text="签到系统", font=font.Font(family='KaiTi', size=35, weight=font.BOLD))
        self.main_label.pack(pady=30)
        
        # 班级选择部分
        self.class_frame = Frame(self.window_name)
        self.class_frame.pack(fill=X)

        # 设置一种字体
        self.combobox_font = font.Font(family='KaiTi', size=20)

        # 选择老师
        self.teacher_frame = Frame(self.class_frame)
        self.teacher_frame.pack(fill=X, side=TOP, expand=YES, pady=10)
        self.teacher_label = Label(self.teacher_frame, text="老师：", font=self.combobox_font)
        self.teacher_label.pack(expand=YES, side=LEFT, anchor=E, pady=10)
        self.teacher_combobox = ttk.Combobox(self.teacher_frame, state="readonly", font=self.combobox_font)
        self.init_teacher()

        # 当选择了某个老师的时候，将班级的下拉框根据选择的老师进行初始化
        self.teacher_combobox.bind("<<ComboboxSelected>>", self.init_current_class)

        # 选择班级
        self.week_frame = Frame(self.class_frame)
        self.week_frame.pack(fill=X, side=BOTTOM, expand=YES, pady=10)
        self.week_label = Label(self.week_frame, text="班级：", font=self.combobox_font)
        self.week_label.pack(expand=YES, side=LEFT, anchor=E, pady=10)
        self.week_combobox = ttk.Combobox(self.week_frame, state="readonly", font=self.combobox_font)
        self.week_combobox.configure(width=25)
        self.week_combobox.pack(expand=YES, side=RIGHT, anchor=W, pady=10)
        # 当某个班级被选择的时候，自动根据选择的班级，将班级内学生在下面进行显示
        self.week_combobox.bind("<<ComboboxSelected>>", self.load_student)

        # 设置下拉框的字体（并不是下拉框选中的内容的字体，所以不会影响到下拉框本身大小）
        self.window_name.option_add("*TCombobox*Listbox*Font", self.combobox_font)
        
        # 学生部分的显示和签到框体
        self.attentance_frame = Frame(self.window_name)
        self.attentance_frame.pack(expand=YES, fill=X)
        
        # 创建两行显示学生的框体，每行四个
        self.attentance_line1_frame = Frame(self.attentance_frame)
        self.attentance_line1_frame.pack(expand=YES, fill=X, padx=50, pady=40)
        self.attentance_line2_frame = Frame(self.attentance_frame)
        self.attentance_line2_frame.pack(expand=YES, fill=X, padx=50, pady=40)

        # 设置提交按钮
        self.submit_button = Button(self.window_name, text='提交出勤记录', bd=2, font=self.combobox_font, command=self.submit_attendance)
        self.submit_button.pack(expand=YES)
    
    def init_teacher(self, event=None):
        """从服务器获取老师的信息，并将其显示在下拉框内"""
        self.teacher_id_name_mapping = dict(submit_sql("select teacher_id, teacher_name from teacher;"))
        self.teacher_combobox["values"] = list(self.teacher_id_name_mapping.values())
        self.teacher_combobox.pack(expand=YES, side=RIGHT, anchor=W, pady=10)

    def init_current_class(self, event=None):
        """初始化当前班级，根据选择的老师，从服务器获取班级，并将结果加入下拉框
        根据当前时间，将当前小时和当前小时-1的班级自动默认从下拉框中选择"""
        teacher_name = self.teacher_combobox.get()
        if not teacher_name:
            return 0
        # 字典的键位班级日期，值为班级名称
        class_info = dict(submit_sql(f"select class_date, class_name from class, teacher where teacher.teacher_id=class.teacher_id and teacher.teacher_name='{teacher_name}';"))
        
        # 由于 strftime 获取的周几的内容是英文，将其转换为中文，创建转换表
        self.zn_ch_week_mapping = {
            "Mon": "周一",
            "Tue": "周二",
            "Web": "周三",
            "Thu": "周四",
            "Fri": "周五",
            "Sat": "周六",
            "Sun": "周日"
            }
        
        # 获取当前时间的周几的内容和当前小时数，将周几转化为中文，将小时数转化为整数
        now_week, now_hour = time.strftime("%a-%H").split('-')
        now_week = self.zn_ch_week_mapping[now_week]
        now_hour = int(now_hour)
        
        # 根据当前时间来选择当前时间对应的班级或者当前时间前一个小时对应的班级，并在遍历获取的班级的时候将班级信息全部放入下拉框
        current_index = 0
        week_values = []
        temp_times = 0
        for k, v in class_info.items():
            week_values.append(v)
            if k == f"{now_week} {now_hour}" or k==f"{now_week} {now_hour-1 if now_hour!=0 else 23}":
                current_index = temp_times
            temp_times += 1
        self.week_combobox["values"] = week_values
        self.week_combobox.current(current_index)
        
        # 读取对应班级的学生
        self.load_student()
    
    def load_student(self, event=None):
        """根据选择的班级获取这个班级对应的学生，在显示学生之前需要先清除所有已有的学生框体"""
        class_name = self.week_combobox.get()
        student_name_list = submit_sql(f"select student_id, student_name from student, class where class.class_id=student.class_id and class.class_name='{class_name}';")
        
        try:
            for i in self.student_list:
                for j in i[:-1]:
                    j.destroy()
        except AttributeError as e:
            print(e)
        
        self.student_list = []

        # 创建每一个学生框体并显示
        for i in range(len(student_name_list)):
            if i<4:
                student_frame = Frame(self.attentance_line1_frame)
            else:
                student_frame = Frame(self.attentance_line2_frame)
            student_frame.pack(expand=True, side=LEFT)
            student_label = Label(student_frame, text=student_name_list[i][1], font=font.Font(family='KaiTi', size=30))
            student_label.pack(side=TOP, anchor=N, pady=15)
            student_combobox = ttk.Combobox(student_frame, state="readonly")
            student_combobox.pack(side=BOTTOM, anchor=S, pady=15)
            student_combobox["values"] = ["出席", "未出席"]

            self.window_name.option_add("*TCombobox*Listbox*Font", self.combobox_font)
            
            # 将所有创建的框体存储进入列表，以便于之后进行操作，特殊的，列表最后一位是学生对应的 id
            self.student_list.append([student_frame, student_label, student_combobox, student_name_list[i][0]])
        
    def submit_attendance(self):
        """将签到信息提交到服务器上，如果有学生没有写任何签到信息，则特殊提示，暂时支持出勤和未出勤两种，暂不支持备注"""
        for i in self.student_list:
            if not i[2].get():
                if askyesno("警告", "存在未填写出勤信息的学生，是否继续？"):
                    break
                else:
                    return 0

        sql = "insert into attendance (class_id, student_id, attendance_date, status) values "
        # current_time = time.strftime("%Y年%m月%d日-%a")
        # arithmetic_mapping = {
        #     "周一": 0,
        #     "周二": 1,
        #     "周三": 2,
        #     "周四": 3,
        #     "周五": 4,
        #     "周六": 5,
        #     "周日": 6
        #     }
        # anti_arithmetic_mapping = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        # target_date = arithmetic_mapping[self.week_combobox.get().split[0]]
        # current_date = arithmetic_mapping[current_time.split('-')[-1]]
        # for i in range(7):
        #     if current_date%7!=target_date:
        #         temp += 1
        #     else:
        #         break
        # curr


        for i in self.student_list:
            info = submit_sql(f"select student.class_id, student.student_id from student, class where student.class_id=class.class_id and student.student_id={i[3]} and class.class_name='{self.week_combobox.get()}'")[0]
            current_time, current_week = time.strftime("%Y/%m/%d-%a").split('-')
            print(current_time)
            current_time = list(map(int, current_time.split('/')))
            arithmetic_mapping = {
            "周一": 0,
            "周二": 1,
            "周三": 2,
            "周四": 3,
            "周五": 4,
            "周六": 5,
            "周日": 6
            }
            anti_arithmetic_mapping = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            current_week = arithmetic_mapping[self.zn_ch_week_mapping[current_week]]
            # 避免签到的时候并不是在上课的时候，而是在上课之后
            for j in range(7):
                current_week = current_week if current_week-j>=0 else current_week+7
                print(arithmetic_mapping[self.week_combobox.get().split()[0]], current_week-j)
                if current_week-j == arithmetic_mapping[self.week_combobox.get().split()[0]]:
                    # 日借位
                    if current_time[2]-j <= 0:
                        # 大月
                        if current_time[1] in (1, 3, 5, 7, 8, 10, 12):
                            # 月借位
                            if current_time[1] == 1:
                                current_time[0] -= 1
                                current_time[1] = 12
                            # 计算日
                            current_time[2] = current_time[2]+31-j
                        # 小月
                        elif current_time[1] in (4, 6, 9, 11):
                            current_time[2] = current_time[2]+30-j
                        # 闰月
                        elif current_time[1] == 2:
                            if is_leap_year(current_time[0]):
                                current_time[2] = current_time[2]+29-j
                            else:
                                current_time[2] = current_time[2]+28-j
                    else:
                        current_time[2] -= j
                    
                    current_time = f"{current_time[0]}年{current_time[1]}月{current_time[2]}日"

                    sql += f"({info[0]}, {info[1]}, '{current_time}', '{i[2].get()}'), "
        
        sql = sql[:-2] + ';'
        print(sql)
        r = submit_sql(sql, mode='post')

        if r==1:
            showinfo("成功", "提交成功！")
        else:
            showinfo("失败", f"提交失败，错误码为：{r}")

def gui_start():
    init_window = Tk()
    ZMJ_PORTAL = MY_GUI(init_window)
    init_window.mainloop()

gui_start()