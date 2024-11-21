# README for Azure Function - Order Processing and Stock Management

## Overview

This project consists of two Azure Functions: 

1. **Order Processing Function**: This function receives HTTP requests to place orders for products. It checks the stock level of the requested product and updates the stock level accordingly. It also sends an event to Azure Event Grid after an order is placed.

2. **Replenishment Event Handler**: This function listens to events from Azure Event Grid. When a stock level for a product drops below a predefined threshold, it schedules a replenishment order and sends an email notification to the relevant person.

## Requirements

### Prerequisites

Before running or deploying the function, ensure the following:

- **Azure Subscription**: You must have an active Azure subscription.
- **Azure Functions Core Tools** (for local development)
- **Python 3.8+** and **pip** (for local development)
- **Required Azure services**:
  - Azure SQL Database
  - Azure Event Grid
  - Azure Communication Services (for email notifications)

### Environment Variables

The following environment variables must be set for the function to run correctly:

1. `SqlConnectionString`: The connection string to the Azure SQL Database.
2. `EVENT_GRID_URL`: The URL of the Event Grid endpoint.
3. `EVENT_GRID_KEY`: The access key for the Event Grid.
4. `ACS_EMAIL_CONNECTION_STRING`: The connection string to the Azure Communication Services (ACS) instance for email sending.
5. `ACS_MAIL_FROM`: The email address used for sending notifications.

The `local.settings.json` file can be used to store local environment variables for local development but need to add to `Application Settings` in the environment variables of the function app.

### Azure Resources

1. **Azure SQL Database**: The database contains the `Products` table, which stores information about products, their stock levels, thresholds for reordering and status of reorder. The database also has `ReplenishemntSchedules` table which holds all scheduled reorders for employees.
2. **Azure Event Grid**: An Event Grid Topic is used to send stock change events to trigger the replenishment process.

## Function 1: Order Processing

### Description

This function is triggered by HTTP requests that contain `product_id` and `quantity` as parameters. It performs the following operations:

1. **Checks Stock Availability**: The function queries the `Products` table to check if the product's stock level is sufficient for the requested quantity.
2. **Stock Update**: If enough stock is available, the function reduces the stock level in the database and commits the changes.
3. **Event Grid Notification**: After successfully updating the stock level, the function sends an event to Event Grid, notifying about the stock level change.

### HTTP Request

- **Method**: `POST`
- **Query Parameters**:
  - `product_id`: The unique ID of the product.
  - `quantity`: The quantity of the product to be ordered.

Example request:

```http
POST https://your-function-url/api/OrderProcessing?product_id=123&quantity=10


```
# Azure Function: Order Processing and Stock Replenishment
## Response

- **Success (200)**: `"Order placed for Product {product_id}. Stock reduced."`
- **Error (404)**: `"Product with ID {product_id} not found."`
- **Error (400)**: `"Not enough stock available for Product {product_id}. Available stock: {stock_level}."`

## SQL Queries

- **SELECT Stock Level**:
  ```sql
  SELECT StockLevel FROM Products WHERE ProductID = ?
   ```
  
- **UPDATE Stock Level**:
  ```sql
  UPDATE Products SET StockLevel = StockLevel - ? WHERE ProductID = ?
  ```

## Function 2: Replenishment Event Handler

### Description

This function is triggered by events from **Azure Event Grid**. It performs the following operations:

1. **Checks Stock Level**:  
   Upon receiving the event, the function retrieves the stock level for the product and compares it to the reorder threshold.

2. **Triggers Replenishment**:  
   If the stock level is below the threshold, it schedules a replenishment and updates the product status to "Pending."

3. **Sends Email Notification**:  
   Once the replenishment is scheduled, the function sends an email to notify the relevant personnel.

## Event Grid Event Schema

The **Event Grid** event contains the following structure:

- **product_id**: The ID of the product.
- **stock_level**: The current stock level of the product.

### Example Event Data:

```json
{
  "id": "unique-event-id",
  "eventTime": "2024-11-21T12:00:00Z",
  "eventType": "StockMonitor",
  "subject": "Product/123",
  "data": {
    "product_id": 123,
    "stock_level": 10
  },
  "dataVersion": "1.0"
}
```

## SQL Queries

### 1. **SELECT Product Threshold and Status:**

This query retrieves the threshold and status for a given product.

```sql
SELECT threshold, status 
FROM Products 
WHERE ProductID = ?
```

### 2. **INSERT Replenishment Schedule:**

This query inserts a new replenishment schedule for a product.

```sql
INSERT INTO ReplenishmentSchedules (ProductID, QuantityNeeded, ScheduledDate) 
VALUES (?, ?, ?)
```

### 3. **UPDATE Product Status:**

This query updates the status of a product in the `Products` table.

```sql
UPDATE Products 
SET Status = ? 
WHERE ProductID = ?
```

### Email Notification

The function uses Azure Communication Services to send an email notification to the responsible person when a replenishment is triggered. The email contains the following information:

- Product ID
- Quantity needed
- Scheduled replenishment date
- Product status

#### Example Email Content:

**Subject:** Replenishment Scheduled for Product 123

**Body:**

```
Dear Employee,

A replenishment of 50 units for Product ID 123 has been scheduled on 2024-11-22 for you to handle. The current status is: Pending.

Thank you for your attention.  
Best regards,  
Your Inventory System
```

