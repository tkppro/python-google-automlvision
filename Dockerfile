FROM node:lts-alpine as fe-build
WORKDIR /app
COPY static/package*.json ./
RUN npm install
COPY static ./
RUN npm run build


FROM python:3.8 as be-build
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY --from=fe-build /app/dist static/dist
EXPOSE 8000
ENV PORT 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
