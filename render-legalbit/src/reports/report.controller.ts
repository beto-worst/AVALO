import { Response,Request } from "express";
import HtmlToPdfService from "./report.service";
export class ReportController {
  public async create(req: Request, res: Response) {
    try {
      const html = req.body?.html || "param 'html' is required";
      res.json( await HtmlToPdfService.render(html,req.body as any))
    } catch (error) {
      console.log(error);
      res.status(500).json({ message: "Server Error ", error});
    }
  }
}
export default  new ReportController();