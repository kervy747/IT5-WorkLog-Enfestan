"""
Reports Controller (MVC)
Handles report generation and data export.
All DB operations via Database singleton using model SQL constants.
Zero UI imports. Returns result tuples for the view to display.
"""

import csv
import os
from datetime import date, datetime
from models.database import db
from models.attendance_model import AttendanceModel
from models.employee_model import EmployeeModel
from models.shift_model import ShiftModel


class ReportsController:
    """Controller for reports generation  pure transaction, zero UI"""

    def __init__(self):
        self.db = db

    def generate_daily_report(self, target_date=None):
        if target_date is None:
            target_date = date.today()
        return self.db.fetch_all(AttendanceModel.Q_GET_ALL_BY_DATE, (target_date,))

    def generate_department_report(self, department, target_date=None):
        if target_date is None:
            target_date = date.today()
        return self.db.fetch_all(AttendanceModel.Q_GET_DEPARTMENT,
                                 (department, target_date))

    def generate_employee_report(self, employee_id, start_date=None, end_date=None):
        employee = self.db.fetch_one(EmployeeModel.Q_SELECT_BY_ID, (employee_id,))
        if start_date and end_date:
            attendance = self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_RANGE,
                                           (employee_id, start_date, end_date))
        else:
            attendance = self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE,
                                           (employee_id,))
        return {'employee': employee, 'attendance': attendance}

    def get_shift_schedule_data(self):
        """Prepare shift schedule report data."""
        employees = self.db.fetch_all(EmployeeModel.Q_SELECT_ALL)
        data = []
        for emp in employees:
            shift = None
            if emp.get('shift_id'):
                shift = self.db.fetch_one(ShiftModel.Q_SELECT_BY_ID,
                                          (emp['shift_id'],))
            data.append({
                'Employee Name': emp.get('full_name', '-'),
                'Department': emp.get('department', '-'),
                'Shift Name': shift.get('shift_name', 'Not Assigned') if shift else 'Not Assigned',
                'Start Time': self._format_shift_time(shift.get('start_time')) if shift else '-',
                'End Time': self._format_shift_time(shift.get('end_time')) if shift else '-',
                'Work Hours': f"{shift.get('work_hours', 8):.1f}" if shift else '-',
                'Grace Period': f"{shift.get('grace_period_mins', 15)} mins" if shift else '-'
            })
        return data

    @staticmethod
    def _format_shift_time(time_val):
        if not time_val:
            return "-"
        from datetime import timedelta
        if isinstance(time_val, timedelta):
            total_seconds = int(time_val.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            time_str = f"{hours:02d}:{minutes:02d}:00"
        else:
            time_str = str(time_val)
        try:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
            return time_obj.strftime('%I:%M %p').lstrip('0')
        except Exception:
            return str(time_val)

    def export_to_csv(self, data, file_path):
        """
        Export data to CSV file.

        Args:
            data: List of records to export
            file_path: Absolute path to write the CSV file

        Returns:
            (success, message)
        """
        if not data:
            return False, "No data available to export."

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if len(data) > 0:
                    headers = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    for record in data:
                        writer.writerow(record)

            return True, f"Report exported successfully to:\n{file_path}"

        except Exception as e:
            return False, f"Failed to export report:\n{str(e)}"

    def export_to_pdf(self, data, file_path, report_title=None, generated_by=None):
        """
        Export data to PDF file.

        Args:
            data: List of records to export
            file_path: Absolute path to write the PDF file
            report_title: Title for the report (optional)

        Returns:
            (success, message)
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            return False, ("PDF export functionality requires reportlab library.\n"
                           "Please install it with: pip install reportlab")

        if not data:
            return False, "No data to export."

        try:
            # Determine report type from filename for customization
            filename = os.path.basename(file_path).lower()
            is_shift_report = 'shift' in filename
            is_daily_report = 'daily' in filename
            is_employee_report = 'employee' in filename

            # Select columns based on report type
            if is_shift_report:
                selected_columns = ['Employee Name', 'Department', 'Shift Name',
                                    'Start Time', 'End Time', 'Work Hours', 'Grace Period']
                title_text = "Work Log - Shift Schedule Report"
            elif is_daily_report:
                selected_columns = ['full_name', 'shift_name', 'date', 'time_in',
                                    'time_out', 'total_hours', 'status']
                title_text = "Work Log - Daily Attendance Report"
            elif is_employee_report:
                selected_columns = ['full_name', 'position', 'department',
                                    'email', 'leave_credits', 'status']
                title_text = "Work Log - Employee Report"
            else:
                selected_columns = list(data[0].keys())[:8]
                title_text = "Work Log - Report"

            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                   leftMargin=0.5*inch, rightMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Heading1'],
                fontSize=18, spaceAfter=20, alignment=1)
            title = Paragraph(title_text, title_style)
            elements.append(title)

            date_style = ParagraphStyle(
                'DateStyle', parent=styles['Normal'],
                fontSize=10, spaceAfter=15, alignment=1)
            date_text = Paragraph(
                f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                date_style)
            elements.append(date_text)

            if generated_by:
                by_style = ParagraphStyle(
                    'ByStyle', parent=styles['Normal'],
                    fontSize=10, spaceAfter=15, alignment=1)
                by_text = Paragraph(f"Generated by: {generated_by}", by_style)
                elements.append(by_text)

            elements.append(Spacer(1, 15))

            available_headers = [c for c in selected_columns if c in data[0]]
            if not available_headers:
                available_headers = list(data[0].keys())[:8]

            clean_headers = [h.replace('_', ' ').title() for h in available_headers]
            table_data = [clean_headers]

            for record in data:
                row = []
                for key in available_headers:
                    value = record.get(key, '')
                    if value is None:
                        value = '-'
                    elif isinstance(value, datetime):
                        value = value.strftime('%I:%M %p')
                    elif isinstance(value, date):
                        value = value.strftime('%Y-%m-%d')
                    elif hasattr(value, 'total_seconds'):
                        total_seconds = int(value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        value = f"{hours:02d}:{minutes:02d}"
                    else:
                        value = str(value) if value else '-'
                    row.append(value)
                table_data.append(row)

            col_count = len(available_headers)
            available_width = 10.5 * inch
            col_width = available_width / col_count

            table = Table(table_data, colWidths=[col_width] * col_count)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5A8AC4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.HexColor('#F8F8F8')]),
            ]))
            elements.append(table)

            elements.append(Spacer(1, 15))
            count_style = ParagraphStyle(
                'CountStyle', parent=styles['Normal'], fontSize=9, alignment=0)
            count_text = Paragraph(f"Total Records: {len(data)}", count_style)
            elements.append(count_text)

            doc.build(elements)
            return True, f"Report exported successfully to:\n{file_path}"

        except Exception as e:
            return False, f"Failed to export PDF: {str(e)}"

    def generate_leave_request_pdf(self, leave_data, file_path, generated_by=None):
        """
        Generate a PDF for a leave request form.

        Args:
            leave_data: Dictionary with leave request details
            file_path: Absolute path to write the PDF file

        Returns:
            (success, message)
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, Paragraph,
                Spacer, Image as RLImage
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        except ImportError:
            return False, ("PDF export requires reportlab.\n"
                           "Install with: pip install reportlab")

        try:
            doc = SimpleDocTemplate(
                file_path, pagesize=A4,
                leftMargin=0.75*inch, rightMargin=0.75*inch,
                topMargin=0.5*inch, bottomMargin=0.5*inch
            )
            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'LeaveTitle', parent=styles['Heading1'],
                fontSize=20, spaceAfter=6, alignment=TA_CENTER,
                textColor=colors.HexColor('#1E293B'))
            subtitle_style = ParagraphStyle(
                'LeaveSubtitle', parent=styles['Normal'],
                fontSize=11, spaceAfter=20, alignment=TA_CENTER,
                textColor=colors.HexColor('#64748B'))
            section_style = ParagraphStyle(
                'SectionHeader', parent=styles['Heading2'],
                fontSize=13, spaceBefore=16, spaceAfter=8,
                textColor=colors.HexColor('#3B82F6'),
                borderPadding=(0, 0, 4, 0))
            normal_style = ParagraphStyle(
                'NormalCustom', parent=styles['Normal'],
                fontSize=10, leading=14)
            bold_style = ParagraphStyle(
                'BoldCustom', parent=styles['Normal'],
                fontSize=10, leading=14, fontName='Helvetica-Bold')

            elements.append(Paragraph("LEAVE REQUEST FORM", title_style))
            elements.append(Paragraph(
                "Work Log Employee Attendance Monitoring System", subtitle_style))

            hr_table = Table([['']], colWidths=[7*inch])
            hr_table.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor('#3B82F6')),
            ]))
            elements.append(hr_table)
            elements.append(Spacer(1, 12))

            status = leave_data.get('status', 'N/A')
            if status == 'Approved':
                status_color = colors.HexColor('#10B981')
            elif status == 'Rejected':
                status_color = colors.HexColor('#EF4444')
            else:
                status_color = colors.HexColor('#F59E0B')

            status_table = Table([[Paragraph(
                f"<b>STATUS: {status.upper()}</b>",
                ParagraphStyle('StatusStyle', parent=styles['Normal'],
                               fontSize=12, alignment=TA_CENTER,
                               textColor=status_color))]],
                colWidths=[3*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, status_color),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
            ]))
            wrapper = Table([[status_table]], colWidths=[7*inch])
            wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(wrapper)
            elements.append(Spacer(1, 16))

            elements.append(Paragraph("Employee Information", section_style))
            emp_data = [
                [Paragraph("<b>Name:</b>", bold_style),
                 Paragraph(str(leave_data.get('full_name', 'N/A')), normal_style)],
                [Paragraph("<b>Department:</b>", bold_style),
                 Paragraph(str(leave_data.get('department', 'N/A')), normal_style)],
                [Paragraph("<b>Leave Credits:</b>", bold_style),
                 Paragraph(f"{leave_data.get('leave_credits', 'N/A')} days", normal_style)],
            ]
            emp_table = Table(emp_data, colWidths=[2*inch, 5*inch])
            emp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(emp_table)
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Leave Details", section_style))
            leave_detail_data = [
                [Paragraph("<b>Leave Type:</b>", bold_style),
                 Paragraph(str(leave_data.get('leave_type', 'N/A')), normal_style)],
                [Paragraph("<b>Start Date:</b>", bold_style),
                 Paragraph(str(leave_data.get('start_date', 'N/A')), normal_style)],
                [Paragraph("<b>End Date:</b>", bold_style),
                 Paragraph(str(leave_data.get('end_date', 'N/A')), normal_style)],
                [Paragraph("<b>Total Days:</b>", bold_style),
                 Paragraph(str(leave_data.get('days_count', 'N/A')), normal_style)],
                [Paragraph("<b>Date Requested:</b>", bold_style),
                 Paragraph(str(leave_data.get('requested_at', 'N/A')), normal_style)],
            ]
            leave_table = Table(leave_detail_data, colWidths=[2*inch, 5*inch])
            leave_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(leave_table)
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Reason for Leave", section_style))
            reason_text = str(leave_data.get('reason', 'No reason provided.'))
            reason_para = Paragraph(reason_text, ParagraphStyle(
                'ReasonStyle', parent=styles['Normal'],
                fontSize=10, leading=14, spaceBefore=4, spaceAfter=4))
            reason_table = Table([[reason_para]], colWidths=[7*inch])
            reason_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(reason_table)
            elements.append(Spacer(1, 12))

            evidence_path = leave_data.get('evidence_path')
            if evidence_path:
                elements.append(Paragraph("Supporting Evidence", section_style))
                full_evidence_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'evidence', evidence_path)
                if os.path.exists(full_evidence_path):
                    try:
                        img = RLImage(full_evidence_path)
                        max_width = 5 * inch
                        max_height = 3.5 * inch
                        img_width = img.drawWidth
                        img_height = img.drawHeight
                        if img_width > max_width:
                            ratio = max_width / img_width
                            img_width = max_width
                            img_height = img_height * ratio
                        if img_height > max_height:
                            ratio = max_height / img_height
                            img_height = max_height
                            img_width = img_width * ratio
                        img.drawWidth = img_width
                        img.drawHeight = img_height
                        elements.append(img)
                    except Exception:
                        elements.append(Paragraph(
                            f"<i>Evidence file attached: {evidence_path}</i>",
                            normal_style))
                else:
                    elements.append(Paragraph(
                        f"<i>Evidence file: {evidence_path} (file not found)</i>",
                        normal_style))
                elements.append(Spacer(1, 12))

            if leave_data.get('reviewed_at'):
                elements.append(Paragraph("Review Information", section_style))
                review_data = [
                    [Paragraph("<b>Reviewed On:</b>", bold_style),
                     Paragraph(str(leave_data.get('reviewed_at', 'N/A')), normal_style)],
                    [Paragraph("<b>Remarks:</b>", bold_style),
                     Paragraph(str(leave_data.get('remarks', 'No remarks')), normal_style)],
                ]
                review_table = Table(review_data, colWidths=[2*inch, 5*inch])
                review_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(review_table)
                elements.append(Spacer(1, 16))

            elements.append(Spacer(1, 30))
            sig_data = [
                [Paragraph("_________________________",
                    ParagraphStyle('SigLine', alignment=TA_CENTER, fontSize=10)),
                 Paragraph("", normal_style),
                 Paragraph("_________________________",
                    ParagraphStyle('SigLine2', alignment=TA_CENTER, fontSize=10))],
                [Paragraph("Employee Signature",
                    ParagraphStyle('SigLabel', alignment=TA_CENTER, fontSize=9,
                                   textColor=colors.HexColor('#64748B'))),
                 Paragraph("", normal_style),
                 Paragraph("Approved By",
                    ParagraphStyle('SigLabel2', alignment=TA_CENTER, fontSize=9,
                                   textColor=colors.HexColor('#64748B')))],
            ]
            sig_table = Table(sig_data, colWidths=[2.8*inch, 1.4*inch, 2.8*inch])
            sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(sig_table)

            elements.append(Spacer(1, 20))
            footer_style = ParagraphStyle(
                'FooterStyle', parent=styles['Normal'],
                fontSize=8, alignment=TA_CENTER,
                textColor=colors.HexColor('#94A3B8'))
            elements.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                f"{' | Generated by: ' + generated_by if generated_by else ''}"
                " | Work Log Employee Attendance Monitoring System", footer_style))

            doc.build(elements)
            return True, f"Leave request PDF saved successfully to:\n{file_path}"

        except Exception as e:
            return False, f"Failed to generate PDF:\n{str(e)}"