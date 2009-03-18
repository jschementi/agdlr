using System;
using System.Web;
using System.IO;
using System.Xml;

namespace Chiron {

    public class XapHttpHandler : IHttpHandler {

        const string XAP_CONTENT_TYPE = "application/x-zip-compressed";

        public bool IsReusable { get { return false; } }

        public void ProcessRequest(HttpContext context) {
            // if there's a XAP file on disk already, simply write it to the 
            // response stream directly
            if (File.Exists(context.Request.PhysicalPath)) {
                context.Response.ContentType = XAP_CONTENT_TYPE;
                context.Response.WriteFile(context.Request.PhysicalPath);
            } else {
                var path = context.Request.Path;
                var vfilename = Path.GetFileNameWithoutExtension(VirtualPathUtility.GetFileName(path));
                var vdirpath = VirtualPathUtility.Combine(VirtualPathUtility.GetDirectory(path), vfilename);
                var pdirpath = context.Server.MapPath(vdirpath);
                
                // create in memory XAP archive
                if (Directory.Exists(pdirpath)) {
                    var xapBuffer = XapBuilder.XapToMemory(pdirpath);
                    context.Response.OutputStream.Write(xapBuffer, 0, xapBuffer.Length);
                } else {
                    throw new HttpException(404, "Missing " + path);
                }
            }
        }
    }
}
