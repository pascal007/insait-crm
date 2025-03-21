# **Flask App**

## **Project Setup & Startup**

### **1. Clone the Repository**
```sh
git clone https://github.com/pascal007/insait-crm
cd insait-crm
```

### **2. Create .env file and add environment variables**

### **3. Build the app**
```sh
docker-compose up
```

## 📌 API Endpoints

### 🔹 **Register a User**
**Endpoint:**  
`POST http://127.0.0.1:5000/api/register`

**Payload:**
```json
{
    "firstname": "Pascal",
    "lastname": "Eze",
    "email": "pascalezeama2@gmail.com",
    "phone": "08140795237",
    "deals": [
        {
            "dealname": "Premium Subscription 2",
            "amount": 199.99,
            "dealstage": "Contract Sent"
        }
    ],
    "tickets": [
        {
            "subject": "Billing Issue - Payment Not Processed",
            "description": "The user was charged but did not receive a confirmation for the premium subscription.",
            "category": "billing",
            "pipeline": "support_pipeline_1",
            "hs_ticket_priority": "MEDIUM",
            "hs_pipeline_stage": 1
        },
        {
            "subject": "Billing Issue - Payment Not Processed 2",
            "description": "The user was charged but did not receive a confirmation for the premium subscription.",
            "category": "billing",
            "pipeline": "support_pipeline_1",
            "hs_ticket_priority": "MEDIUM",
            "hs_pipeline_stage": 1
        }
    ]
}
```

## 📌 API Endpoints

### **Endpoint**
GET http://127.0.0.1:5000/api/new-crm-objects

**Payload:**
```
Parameter	Type	Required	Description
created_after	string	No	Retrieve objects created after this timestamp (ISO 8601 format).
limit	integer	No	Number of objects to return per request (default: 50).
offset	integer	No	Offset for pagination (default: 0).
```


