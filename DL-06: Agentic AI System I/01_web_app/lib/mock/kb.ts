// Mock university knowledge base (fictional content) used by the mock API.
// Mirrors the chunk metadata planned in 05_retrieval_knowledge: status, category, dates.

import type { SourceCategory } from "../types";

export interface KbDoc {
  id: string;
  title_th: string;
  title_en: string;
  category: SourceCategory;
  published_at: string;
  status: "active" | "cancelled" | "superseded";
  superseded_by?: string;
  page: number;
  url: string;
  // Dictionary keywords: stand in for PyThaiNLP tokenization in the mock BM25 ranking.
  keywords: string[];
  content_th: string[];
  content_en: string[];
}

export const KB: KbDoc[] = [
  {
    id: "REG-2026-01",
    title_th: "ระเบียบมหาวิทยาลัยว่าด้วยการลงทะเบียนเรียน ระดับปริญญาตรี พ.ศ. 2569",
    title_en: "University Regulation on Undergraduate Registration B.E. 2569 (2026)",
    category: "regulation",
    published_at: "2026-05-15",
    status: "active",
    page: 2,
    url: "",
    keywords: [
      "ลงทะเบียน", "หน่วยกิต", "เพิ่ม-ถอน", "เพิ่มถอน", "ถอนรายวิชา", "ลงทะเบียนล่าช้า",
      "registration", "register", "credit", "add/drop", "drop", "late registration",
    ],
    content_th: [
      "นักศึกษาต้องลงทะเบียนเรียนภายใน 2 สัปดาห์แรกของภาคการศึกษาปกติ ผ่านระบบทะเบียนออนไลน์",
      "ในภาคการศึกษาปกติ นักศึกษาลงทะเบียนได้ไม่น้อยกว่า 9 หน่วยกิต และไม่เกิน 22 หน่วยกิต",
      "ในภาคฤดูร้อน นักศึกษาลงทะเบียนได้ไม่เกิน 9 หน่วยกิต",
      "การเพิ่ม-ถอนรายวิชาทำได้ภายใน 2 สัปดาห์แรกของภาคการศึกษา โดยไม่ปรากฏรายวิชาในใบแสดงผลการเรียน",
      "การลงทะเบียนล่าช้าทำได้ในสัปดาห์ที่ 3 โดยต้องชำระค่าปรับวันละ 100 บาท",
    ],
    content_en: [
      "Students must register within the first 2 weeks of a regular semester through the online registration system.",
      "In a regular semester, students may register for no fewer than 9 and no more than 22 credits.",
      "In the summer session, students may register for no more than 9 credits.",
      "Courses may be added or dropped within the first 2 weeks of the semester without appearing on the transcript.",
      "Late registration is allowed in week 3 with a fine of 100 baht per day.",
    ],
  },
  {
    // Cancelled: retrieval must never cite it (see 05_retrieval_knowledge, freshness).
    id: "REG-2019-01",
    title_th: "ระเบียบมหาวิทยาลัยว่าด้วยการลงทะเบียนเรียน ระดับปริญญาตรี พ.ศ. 2562 (ยกเลิกแล้ว)",
    title_en: "University Regulation on Undergraduate Registration B.E. 2562 (2019) (cancelled)",
    category: "regulation",
    published_at: "2019-06-01",
    status: "cancelled",
    superseded_by: "REG-2026-01",
    page: 2,
    url: "",
    keywords: ["ลงทะเบียน", "หน่วยกิต", "registration", "register", "credit"],
    content_th: [
      "ในภาคการศึกษาปกติ นักศึกษาลงทะเบียนได้ไม่เกิน 21 หน่วยกิต",
      "การลงทะเบียนล่าช้าต้องชำระค่าปรับวันละ 50 บาท",
    ],
    content_en: [
      "In a regular semester, students may register for no more than 21 credits.",
      "Late registration carries a fine of 50 baht per day.",
    ],
  },
  {
    id: "ANN-2026-07",
    title_th: "ประกาศมหาวิทยาลัย เรื่อง การชำระค่าธรรมเนียมการศึกษา ภาคเรียนที่ 2/2569",
    title_en: "Announcement: Tuition Fee Payment for Semester 2/2026",
    category: "announcement",
    published_at: "2026-11-01",
    status: "active",
    page: 1,
    url: "",
    keywords: [
      "ค่าเทอม", "ค่าธรรมเนียม", "ชำระเงิน", "จ่ายเงิน", "ผ่อนชำระ", "ชำระ", "จ่าย",
      "tuition", "fee", "payment", "pay", "installment",
    ],
    content_th: [
      "ค่าธรรมเนียมการศึกษาแบบเหมาจ่ายระดับปริญญาตรี ภาคเรียนที่ 2/2569 คือ 18,000 บาทต่อภาคเรียน",
      "นักศึกษาต้องชำระค่าธรรมเนียมภายในวันที่ 30 พฤศจิกายน 2569 ผ่าน QR Code ในระบบทะเบียน หรือเคาน์เตอร์ธนาคาร",
      "นักศึกษาที่ชำระหลังกำหนดต้องเสียค่าปรับ 500 บาท และอาจถูกระงับการลงทะเบียน",
      "นักศึกษาที่มีความจำเป็นสามารถยื่นคำร้องขอผ่อนชำระได้ที่กองคลังภายในวันที่ 20 พฤศจิกายน 2569",
    ],
    content_en: [
      "The flat-rate undergraduate tuition fee for semester 2/2026 is 18,000 baht per semester.",
      "Students must pay by 30 November 2026 via the QR code in the registration system or at a bank counter.",
      "Late payment incurs a 500 baht fine and may result in registration being suspended.",
      "Students in need may request an installment plan at the Finance Division by 20 November 2026.",
    ],
  },
  {
    id: "CRS-2026-01",
    title_th: "คู่มือรายวิชา คณะวิทยาศาสตร์ ปีการศึกษา 2569",
    title_en: "Faculty of Science Course Catalog, Academic Year 2026",
    category: "course",
    published_at: "2026-06-01",
    status: "active",
    page: 14,
    url: "",
    keywords: [
      "รายวิชา", "วิชา", "วิชาบังคับก่อน", "prerequisite", "course",
      "cs101", "cs201", "ai301", "math201",
    ],
    content_th: [
      "CS101 การเขียนโปรแกรมเบื้องต้น 3 หน่วยกิต ไม่มีวิชาบังคับก่อน",
      "CS201 โครงสร้างข้อมูล 3 หน่วยกิต วิชาบังคับก่อนคือ CS101",
      "AI301 ปัญญาประดิษฐ์เบื้องต้น 3 หน่วยกิต วิชาบังคับก่อนคือ CS201 และ MATH201",
      "MATH201 พีชคณิตเชิงเส้น 3 หน่วยกิต เปิดสอนทุกภาคการศึกษาปกติ",
    ],
    content_en: [
      "CS101 Introduction to Programming, 3 credits, no prerequisite.",
      "CS201 Data Structures, 3 credits, prerequisite: CS101.",
      "AI301 Introduction to Artificial Intelligence, 3 credits, prerequisites: CS201 and MATH201.",
      "MATH201 Linear Algebra, 3 credits, offered every regular semester.",
    ],
  },
  {
    id: "HB-2026-01",
    title_th: "คู่มือนักศึกษา ระดับปริญญาตรี ปีการศึกษา 2569",
    title_en: "Undergraduate Student Handbook 2026",
    category: "handbook",
    published_at: "2026-07-01",
    status: "active",
    page: 32,
    url: "",
    keywords: [
      "สำเร็จการศึกษา", "จบการศึกษา", "เกียรตินิยม", "เกรดเฉลี่ย", "สอบภาษาอังกฤษ",
      "gpa", "graduation", "graduate", "honors", "honours",
    ],
    content_th: [
      "นักศึกษาจะสำเร็จการศึกษาได้เมื่อเรียนครบตามหลักสูตร และได้เกรดเฉลี่ยสะสมไม่ต่ำกว่า 2.00",
      "นักศึกษาต้องผ่านการทดสอบภาษาอังกฤษ (English Exit Exam) ก่อนสำเร็จการศึกษา",
      "เกียรตินิยมอันดับหนึ่ง: เกรดเฉลี่ยสะสมไม่ต่ำกว่า 3.60 และไม่เคยได้เกรด F หรือเรียนซ้ำรายวิชาใด",
      "เกียรตินิยมอันดับสอง: เกรดเฉลี่ยสะสมไม่ต่ำกว่า 3.25 และไม่เคยได้เกรด F หรือเรียนซ้ำรายวิชาใด",
    ],
    content_en: [
      "Students graduate after completing the program requirements with a cumulative GPA of at least 2.00.",
      "Students must pass the English Exit Exam before graduation.",
      "First-class honors: cumulative GPA of at least 3.60, with no F grade and no repeated course.",
      "Second-class honors: cumulative GPA of at least 3.25, with no F grade and no repeated course.",
    ],
  },
  {
    id: "REG-2026-03",
    title_th: "ระเบียบมหาวิทยาลัยว่าด้วยการลาพักการศึกษา พ.ศ. 2569",
    title_en: "University Regulation on Leave of Absence B.E. 2569 (2026)",
    category: "regulation",
    published_at: "2026-03-10",
    status: "active",
    page: 3,
    url: "",
    keywords: [
      "ลาพัก", "ลาพักการศึกษา", "รักษาสภาพ", "รักษาสถานภาพ", "leave of absence", "leave",
    ],
    content_th: [
      "นักศึกษาขอลาพักการศึกษาได้ครั้งละไม่เกิน 2 ภาคการศึกษาปกติติดต่อกัน",
      "ต้องยื่นคำร้องผ่านระบบทะเบียนก่อนเปิดภาคการศึกษา โดยได้รับความเห็นชอบจากอาจารย์ที่ปรึกษา",
      "นักศึกษาที่ลาพักต้องชำระค่ารักษาสภาพนักศึกษาภาคการศึกษาละ 1,000 บาท",
      "ระยะเวลาที่ลาพักจะนับรวมอยู่ในระยะเวลาการศึกษาตามหลักสูตร",
    ],
    content_en: [
      "Students may take a leave of absence for up to 2 consecutive regular semesters at a time.",
      "Requests must be submitted through the registration system before the semester starts, with the advisor's approval.",
      "Students on leave must pay a status maintenance fee of 1,000 baht per semester.",
      "The leave period counts toward the maximum study duration of the program.",
    ],
  },
  {
    id: "ANN-2026-09",
    title_th: "ประกาศ เรื่อง การรับสมัครทุนการศึกษา ประจำปีการศึกษา 2569",
    title_en: "Announcement: Scholarship Applications for Academic Year 2026",
    category: "announcement",
    published_at: "2026-10-20",
    status: "active",
    page: 1,
    url: "",
    keywords: ["ทุน", "ทุนการศึกษา", "สมัครทุน", "scholarship"],
    content_th: [
      "เปิดรับสมัครทุนการศึกษาระหว่างวันที่ 1-20 ธันวาคม 2569 ผ่านระบบบริการนักศึกษา",
      "ผู้สมัครต้องมีเกรดเฉลี่ยสะสมไม่ต่ำกว่า 2.75 และไม่เคยถูกลงโทษทางวินัย",
      "ทุนประเภทเรียนดีมีมูลค่า 20,000 บาทต่อปีการศึกษา",
      "ประกาศรายชื่อผู้ได้รับทุนภายในวันที่ 15 มกราคม 2570",
    ],
    content_en: [
      "Scholarship applications are open from 1 to 20 December 2026 through the student services portal.",
      "Applicants need a cumulative GPA of at least 2.75 and no disciplinary record.",
      "The academic excellence scholarship is worth 20,000 baht per academic year.",
      "Recipients will be announced by 15 January 2027.",
    ],
  },
];
