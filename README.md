# Python WSGI Proxy to Backend Server

[Online demo](https://proxy.qcloudapps.com/)

## Deploy

### Set environment variables

Development environment

```bash
export BKAPP_UPLOAD_QUERY=upload_query
export BKAPP_UPLOAD_PASSWORD=upload_password
```

Production environment

Set on [Blueking developer center](https://bk.tencent.com/campus/developer-center/)

### Upload go server

Visit <https://proxy.test.qcloudapps.com/upload?upload_query>.

Input password and select file to upload.

Once file uploaded, server will be run automatically.

## License

The MIT License (MIT)

Copyright (c) 2018 Ganlv

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
