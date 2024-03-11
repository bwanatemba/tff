## TFF Political Party Grassroots Registration System

This repository contains a web application designed for the registration of grassroots members for a political party. The system allows users to register as authorized members and sub-members, with the ability to add and manage sub-members under the authorized members.

## Features

**Authorization:** Users can register as authorized members, with unique phone numbers and passwords.
**Sub-Members:** Authorized members can add sub-members, who are associated with their ward and ward position.
**User Management:** The system includes a user loader function for Flask-Login, which retrieves the associated user object given a user ID.

## Models

The application includes the following models:
**AuthorizedMember:** Represents an authorized member with attributes like full name, phone number, constituency, ward, password, and is_super_admin.
**SubMember:** Represents a sub-member with attributes like full name, phone number, constituency, ward, ward_position, and authorized_member_id.

## Forms

The application uses Flask-WTF to define forms for user input:
*SubMemberForm*: A form for sub-member registration with fields for full name, phone number, constituency, ward, and ward_position.

## Database

The application uses SQLAlchemy for database management, with a SQLite database.
