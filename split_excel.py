from io import StringIO, BytesIO
from zipfile import ZipFile

import polars as pl
import streamlit as st

faculty = [f for f in st.text_area("Filenames").split("\n") if f]
count = len(faculty)

if count == 0:
    st.write("No names given")
    st.stop()

st.markdown(f"### Names ({count})\n\n" + "\n".join(f"- {f}" for f in faculty))

excel_inputs = st.file_uploader("Choose a file", accept_multiple_files=True)
if not excel_inputs:
    st.write("Atleast one file must be uploaded")
    st.stop()


output_data = BytesIO()
with ZipFile(output_data, "w") as zip:
    for excel in excel_inputs:
        src_id = excel.name.split(".")[0]
        df = pl.read_excel(
            excel,
            # engine="xlsx2csv",
            engine="openpyxl",
            infer_schema_length=0,
        )
        each_size = df.shape[0] // count
        extras = df.shape[0] % count
        for i in range(count):
            offset, length = each_size * i + (extras > i) * i, each_size + (extras > i)
            print(f"[{src_id}]\t{offset}\t{length}\t{faculty[i]}")
            part = df.slice(offset, length)
            file = BytesIO()
            part.write_excel(file)
            file.seek(0)
            zip.writestr(
                f"{src_id}/{faculty[i]} ({src_id}).xlsx",
                file.read(),
            )

output_data.seek(0)
st.download_button(
    "Download file",
    output_data,
    file_name=(excel.name.rsplit(".", 2)[0] if len(excel_inputs) == 1 else "Parts")
    + ".zip",
)
