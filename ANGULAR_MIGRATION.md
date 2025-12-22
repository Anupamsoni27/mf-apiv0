# Angular App Migration Guide - API URL Update

## 🚀 Backend API Deployed to Azure

The Mutual Fund API has been deployed to Azure App Service (Development Environment).

---

## 📝 Required Changes

### **API Base URL Update**

**Old URL (Local Development):**

```typescript
http://localhost:5000
```

**New URL (Azure Development):**

```typescript
https://stockdash.azurewebsites.net
```

---

## 🔧 Implementation Steps

### 1. **Update Environment Files**

#### `src/environments/environment.ts` (Development)

```typescript
export const environment = {
  production: false,
  apiUrl: "https://stockdash.azurewebsites.net", // Changed from localhost:5000
};
```

#### `src/environments/environment.prod.ts` (Production)

```typescript
export const environment = {
  production: true,
  apiUrl: "https://stockdash.azurewebsites.net", // Same URL for now
};
```

### 2. **Update API Service** (if hardcoded)

If you have hardcoded URLs in any service files, update them:

**Before:**

```typescript
private apiUrl = 'http://localhost:5000';
```

**After:**

```typescript
import { environment } from '../environments/environment';

private apiUrl = environment.apiUrl;
```

---

## ✅ API Endpoints (No Changes)

All endpoint paths remain **exactly the same**:

| Endpoint            | Path                         | Method                 |
| ------------------- | ---------------------------- | ---------------------- |
| **Health Check**    | `/health`                    | GET                    |
| **Get All Stocks**  | `/getAllStocks`              | GET                    |
| **Get Stock Info**  | `/getStockInfo?stock_id=...` | GET                    |
| **Get All Funds**   | `/getAllFunds`               | GET                    |
| **Get Fund Info**   | `/getFundInfo?fund_id=...`   | GET                    |
| **Get Favorites**   | `/api/favorites?userId=...`  | GET                    |
| **Add Favorite**    | `/api/favorites`             | POST                   |
| **Remove Favorite** | `/api/favorites/<item_id>`   | DELETE                 |
| **Users**           | `/api/users`                 | GET, POST, PUT, DELETE |

---

## 🧪 Testing Checklist

After making changes, test these features:

- [ ] User login/authentication
- [ ] Fetching stock list
- [ ] Fetching fund list
- [ ] Stock details page
- [ ] Fund details page
- [ ] Add to favorites
- [ ] Remove from favorites
- [ ] User profile operations

---

## 🔍 Verify Deployment

**Test the health endpoint:**

```bash
curl https://stockdash.azurewebsites.net/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "service": "mf-api",
  "version": "1.0.0"
}
```

---

## 🌐 CORS Configuration

The backend is already configured to accept requests from your Angular app. CORS is enabled for:

- `http://localhost:4200` (local development)
- Your production Angular domain (when deployed)

---

## 📋 Example Service Update

**Before:**

```typescript
// api.service.ts
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";

@Injectable({
  providedIn: "root",
})
export class ApiService {
  private baseUrl = "http://localhost:5000"; // ❌ Old

  constructor(private http: HttpClient) {}

  getStocks() {
    return this.http.get(`${this.baseUrl}/getAllStocks`);
  }
}
```

**After:**

```typescript
// api.service.ts
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "../environments/environment";

@Injectable({
  providedIn: "root",
})
export class ApiService {
  private baseUrl = environment.apiUrl; // ✅ New

  constructor(private http: HttpClient) {}

  getStocks() {
    return this.http.get(`${this.baseUrl}/getAllStocks`);
  }
}
```

---

## 🚨 Breaking Changes

**None!** All endpoints, request formats, and response formats remain identical.

---

## 💡 Tips

1. **Use environment variables** - Never hardcode URLs
2. **Test locally first** - Verify API is accessible before deploying Angular app
3. **Check browser console** - Look for CORS or network errors
4. **Monitor API logs** - Use Azure Portal → Log Stream if issues arise

---

## 📞 Support

**API Endpoints Documentation:** See `AZURE_DEPLOYMENT.md` in backend repository

**API Status:** https://stockdash.azurewebsites.net/health

**Backend Repository:** https://github.com/Anupamsoni27/mf-apiv0

---

## Summary

✅ **Only change required:** Update `apiUrl` from `localhost:5000` to `stockdash.azurewebsites.net` in environment files

✅ **Everything else stays the same:** No endpoint changes, no request/response format changes

✅ **Estimated time:** 5-10 minutes to update and test
