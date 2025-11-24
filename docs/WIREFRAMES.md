# Wireframes & Information Architecture

This document outlines the user personas, user flows, information architecture, and wireframes for the VNPT Talent Hub application.

## 1. User Personas

1.  **Employee (Nhân viên):**
    *   **Goal:** Understand their current competency profile, identify skill gaps, explore career development opportunities, and find relevant training/projects.
    *   **Needs:** A clear, personalized view of their skills, potential career paths, and actionable steps for growth.

2.  **Manager (Quản lý):**
    *   **Goal:** Assess the overall competency of their team, identify skill gaps at a team level, support direct reports' development, and make informed decisions for project staffing.
    *   **Needs:** A dashboard to visualize team strengths/weaknesses, tools to track development progress, and easy access to employee profiles.

3.  **HR Administrator (Quản trị nhân sự):**
    *   **Goal:** Manage the entire competency framework, define job roles and career paths, generate strategic workforce analytics, and ensure data integrity.
    *   **Needs:** Robust admin tools for CRUD operations on competencies, job families, roles, and reporting/analytics features.

## 2. Information Architecture & Navigation

### Primary Navigation

*   **Dashboard:** Personalized landing page for the logged-in user.
*   **My Profile (Hồ sơ của tôi):** Employee's detailed competency view, development plan, and goals.
*   **My Team (Đội của tôi):** (Visible to Managers only) Team overview, individual employee profiles, and development plan approvals.
*   **Career Hub (Lộ trình phát triển):** Tools to explore job families, roles, and career paths.
*   **Admin Panel (Quản trị):** (Visible to HR Admins only) Management of competencies, jobs, users, and system settings.

## 3. Wireframes (Text-based)

### 3.1. Employee Dashboard

*   **Component: Header**
    *   Logo (VNPT Talent Hub)
    *   Primary Navigation Links: [Dashboard] [My Profile] [Career Hub]
    *   User Menu: (User Avatar) -> Dropdown with [Settings] [Logout]

*   **Component: Welcome Banner**
    *   "Welcome, [Employee Name]!"
    *   "Overall Competency Score: [Score] / 5.0" (Visualized with a progress bar)

*   **Component: My Competency Summary (Widget)**
    *   Title: "My Core Competencies"
    *   List of 3-4 key competencies with their current rating (e.g., "Problem Solving: 4/5", "Communication: 3/5").
    *   Link: "-> View All Competencies" (navigates to My Profile)

*   **Component: Recommended for You (Widget)**
    *   Title: "Development Opportunities"
    *   List of 2-3 recommended courses, projects, or mentors based on skill gaps.
    *   Each item shows: Title, Type (Course/Project), and a "View Details" button.

*   **Component: My Career Path (Widget)**
    *   Title: "Next Step in Your Career"
    *   Shows the next likely role in their career path.
    *   Example: "Current: Junior Developer -> Next: Senior Developer"
    *   Link: "-> Explore Career Paths" (navigates to Career Hub)

### 3.2. Employee Profile Page (Tab-based Interface)

*   **Component: Profile Header**
    *   Avatar, Employee Name, Job Title ("Senior Python Developer"), Department.

*   **Tab 1: Competency Profile (Default View)**
    *   Section: Core Competencies
        *   List of all core competencies, each with:
            *   Competency Name
            *   Proficiency Level (e.g., 4/5) visualized with a bar.
            *   Button: "Add Goal"
    *   Section: Functional Competencies
        *   Similar list for functional skills.
    *   Section: Leadership Competencies
        *   Similar list for leadership skills.

*   **Tab 2: Development Plan**
    *   Section: In-Progress Goals
        *   List of goals the employee is currently working on.
        *   Each item: Goal Description, Due Date, Status (In Progress, Completed), Progress bar.
    *   Section: Completed Goals
        *   History of completed development goals.

*   **Tab 3: Feedback**
    *   A view for 360-degree feedback (placeholder for future implementation).

### 3.3. Manager Dashboard

*   **Component: Header** (Same as employee, but with "My Team" link)
    *   Nav Links: [Dashboard] [My Profile] [My Team] [Career Hub]

*   **Component: Team Overview (Widget)**
    *   Title: "My Team's Competency Health"
    *   Metric: "Average Competency Score: [Score] / 5.0"
    *   Metric: "Top 3 Strengths: [Skill 1], [Skill 2], [Skill 3]"
    *   Metric: "Top 3 Gaps: [Skill A], [Skill B], [Skill C]"
    *   Link: "-> Go to Team View"

*   **Component: Pending Approvals (Widget)**
    *   Title: "Action Required"
    *   List of items needing manager's approval.
    *   Example: "[Employee Name]'s Development Plan - Ready for review"
    *   Buttons: [Approve] [Reject]

*   **Component: Team Member Spotlight (Widget)**
    *   Title: "Team Members"
    *   A list/grid of direct reports with their photo, name, and overall competency score.
    *   Clicking a member navigates to their profile (Manager's view).

### 3.4. Manager Team View

*   **Component: Main View - Competency Matrix**
    *   A table/grid view:
        *   Rows: Team Members (Name)
        *   Columns: Key Competencies (e.g., Python, Project Management, Communication)
        *   Cells: Proficiency score (e.g., "4/5"), color-coded for quick visual assessment (e.g., Red for low, Green for high).
*   **Component: Filters**
    *   Filter by Job Family (e.g., "Show all Engineers")
    *   Filter/Search for specific competencies.
*   **Component: Summary View (Sidebar)**
    *   Displays aggregate data for the filtered view.
    *   "Team Average for 'Python': 3.8/5"
    *   "Highest Score for 'Python': [Employee Name] (5/5)"
