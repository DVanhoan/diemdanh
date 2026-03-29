-- Attendance System Database Schema
-- MySQL 8+

CREATE DATABASE IF NOT EXISTS attendance_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE attendance_system;

-- --------------------------------------------------------------------------
-- Core tables from the report/images
-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `Class` (
  `Class` VARCHAR(45) NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Class`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Teacher` (
  `Teacher_id` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `Phone` VARCHAR(45) NOT NULL,
  `Email` VARCHAR(45) NOT NULL,
  `SecurityQ` VARCHAR(45) NOT NULL,
  `SecurityA` VARCHAR(45) NOT NULL,
  `Password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Teacher_id`),
  UNIQUE KEY `uk_teacher_email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Subject` (
  `Subject_id` INT NOT NULL AUTO_INCREMENT,
  `Subject_name` VARCHAR(45) NOT NULL,
  `Class` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Subject_id`),
  KEY `idx_subject_class` (`Class`),
  CONSTRAINT `fk_subject_class`
    FOREIGN KEY (`Class`) REFERENCES `Class` (`Class`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Account` (
  `Account` VARCHAR(45) NOT NULL,
  `Password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Student table is required to support Student_id foreign keys
-- (Student_id appears in Attendance and Student_Subject designs).
CREATE TABLE IF NOT EXISTS `Student` (
  `Student_id` INT NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  `Class` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Student_id`),
  KEY `idx_student_class` (`Class`),
  CONSTRAINT `fk_student_class`
    FOREIGN KEY (`Class`) REFERENCES `Class` (`Class`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Lesson` (
  `Lesson_id` INT NOT NULL AUTO_INCREMENT,
  `Time_start` TIME NULL,
  `Time_end` TIME NULL,
  `Date` DATE NOT NULL,
  `Teacher_id` INT NOT NULL,
  `Subject_id` INT NOT NULL,
  PRIMARY KEY (`Lesson_id`),
  KEY `idx_lesson_teacher` (`Teacher_id`),
  KEY `idx_lesson_subject` (`Subject_id`),
  CONSTRAINT `fk_lesson_teacher`
    FOREIGN KEY (`Teacher_id`) REFERENCES `Teacher` (`Teacher_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT `fk_lesson_subject`
    FOREIGN KEY (`Subject_id`) REFERENCES `Subject` (`Subject_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Attendance` (
  `IdAttendance` VARCHAR(45) NOT NULL,
  `Student_id` INT NULL,
  `Name` VARCHAR(45) NULL,
  `Class` VARCHAR(45) NULL,
  `Time_in` TIME NULL,
  `Time_out` TIME NULL,
  `Date` DATE NULL,
  `Lesson_id` INT NULL,
  `AttendanceStatus` VARCHAR(45) NULL,
  PRIMARY KEY (`IdAttendance`),
  KEY `idx_attendance_student` (`Student_id`),
  KEY `idx_attendance_lesson` (`Lesson_id`),
  KEY `idx_attendance_date` (`Date`),
  CONSTRAINT `fk_attendance_student`
    FOREIGN KEY (`Student_id`) REFERENCES `Student` (`Student_id`)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT `fk_attendance_lesson`
    FOREIGN KEY (`Lesson_id`) REFERENCES `Lesson` (`Lesson_id`)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT `fk_attendance_class`
    FOREIGN KEY (`Class`) REFERENCES `Class` (`Class`)
    ON UPDATE CASCADE
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Student_Subject` (
  `Student_id` INT NOT NULL,
  `Subject_id` INT NOT NULL,
  PRIMARY KEY (`Student_id`, `Subject_id`),
  KEY `idx_student_subject_subject` (`Subject_id`),
  CONSTRAINT `fk_student_subject_student`
    FOREIGN KEY (`Student_id`) REFERENCES `Student` (`Student_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_student_subject_subject`
    FOREIGN KEY (`Subject_id`) REFERENCES `Subject` (`Subject_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `Teacher_Subject` (
  `Teacher_id` INT NOT NULL,
  `Subject_id` INT NOT NULL,
  PRIMARY KEY (`Teacher_id`, `Subject_id`),
  KEY `idx_teacher_subject_subject` (`Subject_id`),
  CONSTRAINT `fk_teacher_subject_teacher`
    FOREIGN KEY (`Teacher_id`) REFERENCES `Teacher` (`Teacher_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_teacher_subject_subject`
    FOREIGN KEY (`Subject_id`) REFERENCES `Subject` (`Subject_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------------------------
-- Seed default teacher account for first-time login testing
-- Email: admin@gmail.com
-- Password: 123
-- --------------------------------------------------------------------------
INSERT INTO `Teacher` (`Name`, `Phone`, `Email`, `SecurityQ`, `SecurityA`, `Password`)
VALUES ('admin', '0000000000', 'admin@gmail.com', 'default', 'default', '123')
ON DUPLICATE KEY UPDATE
  `Name` = VALUES(`Name`),
  `Phone` = VALUES(`Phone`),
  `SecurityQ` = VALUES(`SecurityQ`),
  `SecurityA` = VALUES(`SecurityA`),
  `Password` = VALUES(`Password`);
