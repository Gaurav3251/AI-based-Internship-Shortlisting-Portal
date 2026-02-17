import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home.jsx';
import Login from './auth/Login.jsx';
import Register from './auth/Register.jsx';
import NotFound from './pages/NotFound.jsx';
import Forbidden from './pages/Forbidden.jsx';
import RequireAuth from './auth/RequireAuth.jsx';
import RoleGuard from './auth/RoleGuard.jsx';
import StudentLayout from './student/StudentLayout.jsx';
import StudentDashboard from './student/StudentDashboard.jsx';
import StudentProfile from './student/StudentProfile.jsx';
import EditStudentProfile from './student/EditStudentProfile.jsx';
import ApplyInternship from './student/ApplyInternship.jsx';
import MyApplications from './student/MyApplications.jsx';
import TeacherLayout from './teacher/TeacherLayout.jsx';
import TeacherDashboard from './teacher/TeacherDashboard.jsx';
import PostInternship from './teacher/PostInternship.jsx';
import ViewInternships from './teacher/ViewInternships.jsx';
import EditInternship from './teacher/EditInternship.jsx';
import ShortlistedStudents from './teacher/ShortlistedStudents.jsx';
import Analytics from './teacher/Analytics.jsx';
import TeacherProfile from './teacher/TeacherProfile.jsx';

const App = () => (
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />

    <Route
      path="/student"
      element={
        <RequireAuth>
          <RoleGuard role="student">
            <StudentLayout />
          </RoleGuard>
        </RequireAuth>
      }
    >
      <Route index element={<Navigate to="/student/dashboard" />} />
      <Route path="dashboard" element={<StudentDashboard />} />
      <Route path="profile" element={<StudentProfile />} />
      <Route path="profile/edit" element={<EditStudentProfile />} />
      <Route path="apply/:internshipId" element={<ApplyInternship />} />
      <Route path="applications" element={<MyApplications />} />
    </Route>

    <Route
      path="/teacher"
      element={
        <RequireAuth>
          <RoleGuard role="teacher">
            <TeacherLayout />
          </RoleGuard>
        </RequireAuth>
      }
    >
      <Route index element={<Navigate to="/teacher/dashboard" />} />
      <Route path="dashboard" element={<TeacherDashboard />} />
      <Route path="profile" element={<TeacherProfile />} />
      <Route path="internships/new" element={<PostInternship />} />
      <Route path="internships" element={<ViewInternships />} />
      <Route path="internships/:internshipId/edit" element={<EditInternship />} />
      <Route path="shortlisted/:internshipId" element={<ShortlistedStudents />} />
      <Route path="analytics" element={<Analytics />} />
    </Route>

    <Route path="/403" element={<Forbidden />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default App;
