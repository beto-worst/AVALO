import express, { Express,Response,Request } from 'express';
import dotenv from 'dotenv';
import  ReportController  from './reports/report.controller';
dotenv.config();
const app: Express = express();
app.use(express.json()); //Parse URL-encoded bodies

const port = process.env.PORT || 3001;
app.get('/', (req: Request, res: Response) => {
    console.log("Welcome!");
    res.json({message:"Welcome"});
});
app.post('/report', (req, res)=>{
    ReportController.create(req, res)
});

app.listen(port, () => {
  console.log(`⚡️[server]: Server is running at http://localhost:${port}`);
});