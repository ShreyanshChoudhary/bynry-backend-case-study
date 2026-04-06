#  Backend Engineering Case Study

Hi, I'm Shreyansh 👋  
This repository contains my solution to a backend engineering case study focused on designing a scalable inventory management system.

> Designed with focus on data integrity, auditability, and real-world backend constraints.



## What I Built

The goal was to design a system that can:

- Manage products across multiple warehouses  
- Track inventory levels accurately  
- Maintain a complete audit trail of stock changes  
- Handle real-world constraints like data consistency and validation  



##  Key Features

###  Product & Inventory Management
- Create products with proper validation  
- Assign products to warehouses  
- Maintain inventory per warehouse  

###  Audit Logging
- Every inventory change is recorded in `inventory_transactions`  
- Includes initial stock using `INITIAL_LOAD`  
- Designed as append-only for full traceability  

###  Data Integrity
- Transaction-safe operations  
- Input validation for all critical fields  
- Duplicate product checks  



## Tech Stack

- **Python (Flask)** → used for debugging and prototyping  
- **PostgreSQL** → reliable relational database  
- **SQL (Parameterized Queries)** → prevents SQL injection  



##  Design Decisions

### Why separate `inventory` and `inventory_transactions`?

I separated current state from history:

- `inventory` → stores latest stock (fast access)  
- `inventory_transactions` → stores all changes (audit log)  

This helps in:
- Better performance  
- Easy debugging  
- Complete historical tracking  



### Why use transactions?

All operations (product creation + inventory update + audit log) are done inside a single transaction.

This ensures:
- No partial updates  
- Strong consistency  
- Safe rollback on failure  



### Why audit logging?

In real-world systems, stock mismatches happen often.

Audit logs help:
- Track what changed and when  
- Debug issues quickly  
- Maintain accountability  



## Real-World Considerations

While designing this system, I considered:

- Handling concurrent updates (can be improved using optimistic locking)  
- Using connection pooling in production  
- Query optimization for large datasets  



## Note

Flask was used here mainly for quick debugging and demonstration.  
The design reflects how I would implement this in a production backend system.



## Repository Contents
Backend_Case_Study_Bynry.docx
corrected_app.py




## Final Thoughts

I focused on keeping the system:
- Practical  
- Scalable  
- Easy to understand  


Thanks for reviewing this 
