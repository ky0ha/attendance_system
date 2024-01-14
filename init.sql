-- SELECT name FROM sqlite_master WHERE type='table';

DROP TABLE student;
DROP TABLE teacher;
DROP TABLE course;
DROP TABLE period;

CREATE TABLE student (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    sname TEXT NOT NULL,
    period INTEGER NOT NULL
);

CREATE TABLE teacher (
    tno INTEGER PRIMARY KEY AUTOINCREMENT,
    tname TEXT NOT NULL
);

CREATE TABLE course (
    cno INTEGER PRIMARY KEY AUTOINCREMENT,
    cname TEXT NOT NULL,
    credit INTEGER NOT NULL
);


CREATE TABLE period (
    record_no INTEGER PRIMARY KEY AUTOINCREMENT,
    sno INTEGER NOT NULL,
    cno INTEGER NOT NULL,
    tno INTEGER NOT NULL,
    record_time INTEGER NOT NULL,
    FOREIGN KEY (sno) REFERENCES student(sno),
    FOREIGN KEY (cno) REFERENCES course(cno),
    FOREIGN KEY (tno) REFERENCES course(tno)
);
