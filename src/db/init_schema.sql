/*
 Navicat Premium Data Transfer

 Source Server         : main
 Source Server Type    : MySQL
 Source Server Version : 80035 (8.0.35)
 Source Host           : localhost:3306
 Source Schema         : attendance_system

 Target Server Type    : MySQL
 Target Server Version : 80035 (8.0.35)
 File Encoding         : 65001

 Date: 29/03/2026 16:21:53
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin`  (
  `Account` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Password` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Account`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for attendance
-- ----------------------------
DROP TABLE IF EXISTS `attendance`;
CREATE TABLE `attendance`  (
  `IdAttendance` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Student_id` int NOT NULL,
  `Name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Class` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Time_in` time NULL DEFAULT NULL,
  `Time_out` time NULL DEFAULT NULL,
  `Date` date NULL DEFAULT NULL,
  `Lesson_id` int NOT NULL,
  `AttendanceStatus` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`IdAttendance`) USING BTREE,
  INDEX `idx_attendance_student`(`Student_id` ASC) USING BTREE,
  INDEX `idx_attendance_lesson`(`Lesson_id` ASC) USING BTREE,
  INDEX `idx_attendance_date`(`Date` ASC) USING BTREE,
  INDEX `fk_attendance_class`(`Class` ASC) USING BTREE,
  CONSTRAINT `fk_attendance_class` FOREIGN KEY (`Class`) REFERENCES `class` (`Class`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_lesson` FOREIGN KEY (`Lesson_id`) REFERENCES `lesson` (`Lesson_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_student` FOREIGN KEY (`Student_id`) REFERENCES `student` (`Student_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for class
-- ----------------------------
DROP TABLE IF EXISTS `class`;
CREATE TABLE `class`  (
  `Class` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Class`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for lesson
-- ----------------------------
DROP TABLE IF EXISTS `lesson`;
CREATE TABLE `lesson`  (
  `Lesson_id` int NOT NULL AUTO_INCREMENT,
  `Time_start` time NULL DEFAULT NULL,
  `Time_end` time NULL DEFAULT NULL,
  `Date` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Teacher_id` int NOT NULL,
  `Subject_id` int NOT NULL,
  PRIMARY KEY (`Lesson_id`) USING BTREE,
  INDEX `idx_lesson_teacher`(`Teacher_id` ASC) USING BTREE,
  INDEX `idx_lesson_subject`(`Subject_id` ASC) USING BTREE,
  CONSTRAINT `fk_lesson_subject` FOREIGN KEY (`Subject_id`) REFERENCES `subject` (`Subject_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_lesson_teacher` FOREIGN KEY (`Teacher_id`) REFERENCES `teacher` (`Teacher_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student`  (
  `Student_id` int NOT NULL,
  `Dep` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `course` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Year` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Semester` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Class` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Roll` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Gender` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Dob` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Email` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Phone` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `PhotoSample` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`Student_id`) USING BTREE,
  INDEX `idx_student_class`(`Class` ASC) USING BTREE,
  CONSTRAINT `fk_student_class` FOREIGN KEY (`Class`) REFERENCES `class` (`Class`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student_has_subject
-- ----------------------------
DROP TABLE IF EXISTS `student_has_subject`;
CREATE TABLE `student_has_subject`  (
  `Student_id` int NOT NULL,
  `Subject_id` int NOT NULL,
  PRIMARY KEY (`Student_id`, `Subject_id`) USING BTREE,
  INDEX `idx_student_subject_subject`(`Subject_id` ASC) USING BTREE,
  CONSTRAINT `fk_student_subject_student` FOREIGN KEY (`Student_id`) REFERENCES `student` (`Student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_student_subject_subject` FOREIGN KEY (`Subject_id`) REFERENCES `subject` (`Subject_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for subject
-- ----------------------------
DROP TABLE IF EXISTS `subject`;
CREATE TABLE `subject`  (
  `Subject_id` int NOT NULL AUTO_INCREMENT,
  `Subject_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Class` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Subject_id`) USING BTREE,
  INDEX `idx_subject_class`(`Class` ASC) USING BTREE,
  CONSTRAINT `fk_subject_class` FOREIGN KEY (`Class`) REFERENCES `class` (`Class`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teacher
-- ----------------------------
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher`  (
  `Teacher_id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Phone` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Email` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `SecurityQ` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `SecurityA` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Password` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Teacher_id`) USING BTREE,
  UNIQUE INDEX `uk_teacher_email`(`Email` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 52 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teacher_has_subject
-- ----------------------------
DROP TABLE IF EXISTS `teacher_has_subject`;
CREATE TABLE `teacher_has_subject`  (
  `Teacher_id` int NOT NULL,
  `Subject_id` int NOT NULL,
  PRIMARY KEY (`Teacher_id`, `Subject_id`) USING BTREE,
  INDEX `idx_teacher_subject_subject`(`Subject_id` ASC) USING BTREE,
  CONSTRAINT `fk_teacher_subject_subject` FOREIGN KEY (`Subject_id`) REFERENCES `subject` (`Subject_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_teacher_subject_teacher` FOREIGN KEY (`Teacher_id`) REFERENCES `teacher` (`Teacher_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;



INSERT INTO `Teacher` (`Name`, `Phone`, `Email`, `SecurityQ`, `SecurityA`, `Password`)
VALUES ('admin', '0000000000', 'admin@gmail.com', 'default', 'default', '123')
ON DUPLICATE KEY UPDATE
  `Name` = VALUES(`Name`),
  `Phone` = VALUES(`Phone`),
  `SecurityQ` = VALUES(`SecurityQ`),
  `SecurityA` = VALUES(`SecurityA`),
  `Password` = VALUES(`Password`);