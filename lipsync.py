import os, asyncio
from gradio_client import Client, handle_file

DEFAULT_SPACE="henrybit/SadTalker-Demo"

async def make_lipsync(image,audio,outfile):
    space=os.getenv("LIPSYNC_SPACE",DEFAULT_SPACE)
    token=os.getenv("HF_TOKEN") or None
    client=Client(space,token=token)

    # The public Space exposes a SadTalker generate/test endpoint.
    # Try the common Gradio endpoint first, then the legacy name.
    candidates=["/generate","/predict"]
    last=None
    for api in candidates:
        try:
            result=client.predict(
                handle_file(str(image)),
                handle_file(str(audio)),
                "full",       # preprocess_type
                False,        # still mode
                False,        # enhancer
                2,            # batch size
                256,          # resolution
                0,            # pose
                "facevid2vid",
                1,            # expression
                False,        # reference video
                None,
                "pose",
                False,
                5,
                True,
                api_name=api
            )
            # Gradio may return a path or FileData object.
            path = result[0] if isinstance(result,(list,tuple)) else result
            if hasattr(path,"path"): path=path.path
            import shutil
            shutil.copyfile(str(path),str(outfile))
            return outfile
        except Exception as e:
            last=e
    raise RuntimeError(
        "Free lip-sync Space could not process this scene. "
        "It may be busy or its API schema may have changed. "
        f"Last error: {last}"
    )
