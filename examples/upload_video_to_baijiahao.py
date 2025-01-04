import asyncio
from datetime import datetime
from pathlib import Path

# ! 如果要在根目录调用该文件，需要添加以下代码
import sys
# 获取当前文件的父目录（即 'src' 目录）的父目录（即项目根目录）
project_root = Path(__file__).parent.parent.resolve()
# 将项目根目录添加到 Python 的模块搜索路径中
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from conf import BASE_DIR
from uploader.weibo_uploader.main import weibo_setup, WeiBoVideo
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags


if __name__ == '__main__':
    # 以今天日期当做要发布的文件夹
    filepath = Path(BASE_DIR) / "videos" / "backups" / datetime.now().strftime("%Y-%m-%d")
    account_file = Path(BASE_DIR / "cookies" / "weibo_uploader" / "account.json")
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    if file_num == 0:
        raise ValueError("要发布的文件夹或视频不存在")

    publish_datetimes = generate_schedule_time_any_day(file_num, 1,
                                                       daily_times=[6], start_date="1")
    cookie_setup = asyncio.run(weibo_setup(account_file, handle=False))

    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        # 打印视频文件名、标题和 hashtag
        print(f"视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")
        app = WeiBoVideo(title, file, tags, publish_datetimes[index], account_file)
        asyncio.run(app.main(), debug=False)

"""
百家号: https://aigc.baidu.com/make

获取热点推荐:
curl ^"https://aigc.baidu.com/aigc/saas/pc/v1/assist/getHotList?tab=^%^E5^%^A8^%^B1^%^E4^%^B9^%^90^" ^
  -H ^"Accept: */*^" ^
  -H ^"Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7^" ^
  -H ^"Cache-Control: max-age=0^" ^
  -H ^"Connection: keep-alive^" ^
  -H ^"Cookie: BIDUPSID=0F811928FB4726E22A2E94E3E4B3E50D; PSTM=1657455618; MCITY=-^%^3A; BAIDUID=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; H_WISE_SIDS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; H_WISE_SIDS_BFESS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; BAIDUID_BFESS=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; ZFY=LmoYTIFAciytvddeaT:BxhGLNdbGk7zNL43UWd0FmuPc:C; __bid_n=194278bf9e6955295fea9b; H_PS_PSSID=61027_60853_61495_61518_61528_61359_61608_61684_61551; BDUSS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BDUSS_BFESS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BA_HECTOR=0h052k25a42l0ga40424a5a4bn6h0p1jnfvom1u; hot-current-tab=^%^7B^%^22name^%^22^%^3A^%^22^%^E5^%^A8^%^B1^%^E4^%^B9^%^90^%^22^%^2C^%^22index^%^22^%^3A1^%^7D; XFI=a19182d0-caa4-11ef-a8f1-557631737715; saas-appinfo=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..RnIWZgp-un1Rs05b.qY9EQ8lV7QgElJmXb-NjxvcgYIkf3m0GVGd-r2I1ZpgPEZM6AjSoEPqHGm_S6wgrUcC5XcJGlIoPqQGsl86iNHqP2_cgmD--JpUYH60QR6FgCoE6ezosheIjIgFVEwNFyYh1pRtTn0o_fRj5B5qnFBVSoNd4BkJZ84g0AlYxiS7xCUCi1kva5k4RWruZeYs3dAIOnweCXhHjTy35PMaTwyWHBqJahookRI3VxGY8Y8bZ4w3sFsbLwitBbA48AFm_l2Wyqho3B9eutMqTQCqQnJtaP3FzVAOR0rahc3IZKUtpf9ezWxUqgFkJ4R1EOIHtbZoBXFdlenMyg0TQuSanXXc2uJE4vGU3eqwn40NWGi7kLCRoSFXCx6dcEx2rpngVHJtAY2RLXAnw7zK7jfWRNwO6gO82qbGGPaVZw_TAurrlR14A6QCs9e9baHQu1sHv2wwqYZJt3XgGE-VG73HDFUFagaYQ7U05jIeaYUKPMzbTYSlT3zFpLccbALcd5JpKQr04Jg0hFbyO-NOVSuKiXtLvTN6MN_0qAMGXgjf9JbuRuNMgQ6cZzhIwOETR2dryJycBIx1s7GXbubrZkHh9crIS9I8B4Rq_RXSHk2oIcMyrzyBTnaIPCgTVnIWK8589aQeOlGio3sHcTPery8v4Irn7LRryW_9eW5flAqYEhiXabOZc8wHLWb9AaYGMT10X9uitq2rvwnprco8PiaV-ebuYCyKsYK89hGbyU60eEEsbuF2dCxHIHEDnzC1o9GbmSdUIUf9PdmoNHVm7U_ayTr0kVVPignKFJIjhnFODsF_FzzeDZQudG_owpE6gMw0QsJly6rXLAoA09Nm3wavcPHyKSy_l28LUpJ2XDomyIf6V_MPKZ667MBow4Xd62IcJt_iPN5fHVIkqEkIeud6GtVeTik-5x_cju87BOHmC8tsLRd4UzzX0eJpajys619wVow0HGMvuODMlKcTjrC_wfaSRC5P-F2ICdCWJWfbSRy23Nd1nGP0OPonmhxjn9YolaWrktugztbNHrsibF_bguCnleZ1tqwmiYm5KgPHszxO7k9CIBqSUVsqb5ZeTCznU2QM3m_GeXv_RPZujma-4tEWYmSIGCh3W_FvBhi7Z2-Ba5KhCxRVoN9iI-evNomIcECkb0usU-ZwuWMqrxIDxHTIXxKE3JYPwLTj_n-5Ozolf0gTrwx2aJF6vPSySZlutuPArtOeK9-XSKEdP9D0yNZtzYMjYgv9kzH5b7V3IZWINQkPPO8lo7J8OJNhUYBiiOPT1dXBiIvjhzykyFzmC9t0ydZWU3MjtjfkFHTGxZx0hZxdaKjL5Pec1z52XNYxAyAJebR1FCjwbZjPHB8WhKwm3i0qkDIJbeRC9ODmE-fo62Z9PLEJVxpcBBqUoeB5Qp3loOXT1I0ISrYQXKY17-8ejFAnY3yli4j7FvsTsx5wbNpJ3Lkg-hnjPtz0vUzuFVw894NqQ7C2XIVSXjbER5qC7a2xjgHhOB_wPe9ttzfPQkDLncKzgZ5d3C15xakWcA5rZiWxfDS2pP2Ucud_Gx_taQQr6rfzIDstsYrn7ilDBvSgQXbhLLdwhY-t1-85KDF8pIGB_5MhDxTFSKGfr2lwgqqFi9T2-r5Zzh1_ctews4vFMwsMjFa6YAIqyImicEM60ZH7Ews8LCF1DjxWJ8y5xwGRYz8hoyCyfERRz5A3WFr8ZnOAqbDZUfRw65XI147tuw2G2R0RzlDSZggJ3Sji68daA4lzo5bdJ3A1rljClux_sFQWgACRCaQDDzRJBnDcKrEuJMEwwD-A7q2S3aDKeaw-FR4ybj1HZ_sBLgyvpv3NzShdjHXOZZBnjhCAI-RwEDOobjRDWc6xqQbwTk53h2k9rsvnVOp_s7nJpPJxev3nn_2whxedGecGspAvK9LKvvSX-eMSeJVtrTMF5jxR7b9-NLW-HpxMRIF4CeRCydnZ8.hW-30I7CC3Qbh62zI4paCQ; XFCS=8C5BBC1520874DDF83C5FC145B008BED020C813A5E7777A39C62A5101656F3AA; XFT=AVxPgyj7sTVTpdgHkOF+ttrpDXVmiYGJWX731zQ6zYs=; RT=^\^"z=1^&dm=baidu.com^&si=8b3e0efe-71af-4b80-bbb6-2e9a89ba9543^&ss=m5i97sas^&sl=1^&tt=4y^&bcn=https^%^3A^%^2F^%^2Ffclog.baidu.com^%^2Flog^%^2Fweirwood^%^3Ftype^%^3Dperf^&ld=xt^\^"^" ^
  -H ^"Referer: https://aigc.baidu.com/make^" ^
  -H ^"Sec-Fetch-Dest: empty^" ^
  -H ^"Sec-Fetch-Mode: cors^" ^
  -H ^"Sec-Fetch-Site: same-origin^" ^
  -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36^" ^
  -H ^"sec-ch-ua: ^\^"Google Chrome^\^";v=^\^"131^\^", ^\^"Chromium^\^";v=^\^"131^\^", ^\^"Not_A Brand^\^";v=^\^"24^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^"

根据某个热点生成文案:
curl ^"https://aigc.baidu.com/aigc/saas/pc/v1/task/t2t/create^" ^
  -H ^"Accept: */*^" ^
  -H ^"Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7^" ^
  -H ^"Connection: keep-alive^" ^
  -H ^"Content-Type: application/json^" ^
  -H ^"Cookie: BIDUPSID=0F811928FB4726E22A2E94E3E4B3E50D; PSTM=1657455618; MCITY=-^%^3A; BAIDUID=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; H_WISE_SIDS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; H_WISE_SIDS_BFESS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; BAIDUID_BFESS=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; ZFY=LmoYTIFAciytvddeaT:BxhGLNdbGk7zNL43UWd0FmuPc:C; __bid_n=194278bf9e6955295fea9b; H_PS_PSSID=61027_60853_61495_61518_61528_61359_61608_61684_61551; BDUSS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BDUSS_BFESS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BA_HECTOR=0h052k25a42l0ga40424a5a4bn6h0p1jnfvom1u; hot-current-tab=^%^7B^%^22name^%^22^%^3A^%^22^%^E5^%^A8^%^B1^%^E4^%^B9^%^90^%^22^%^2C^%^22index^%^22^%^3A1^%^7D; XFI=a19182d0-caa4-11ef-a8f1-557631737715; saas-appinfo=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..RnIWZgp-un1Rs05b.qY9EQ8lV7QgElJmXb-NjxvcgYIkf3m0GVGd-r2I1ZpgPEZM6AjSoEPqHGm_S6wgrUcC5XcJGlIoPqQGsl86iNHqP2_cgmD--JpUYH60QR6FgCoE6ezosheIjIgFVEwNFyYh1pRtTn0o_fRj5B5qnFBVSoNd4BkJZ84g0AlYxiS7xCUCi1kva5k4RWruZeYs3dAIOnweCXhHjTy35PMaTwyWHBqJahookRI3VxGY8Y8bZ4w3sFsbLwitBbA48AFm_l2Wyqho3B9eutMqTQCqQnJtaP3FzVAOR0rahc3IZKUtpf9ezWxUqgFkJ4R1EOIHtbZoBXFdlenMyg0TQuSanXXc2uJE4vGU3eqwn40NWGi7kLCRoSFXCx6dcEx2rpngVHJtAY2RLXAnw7zK7jfWRNwO6gO82qbGGPaVZw_TAurrlR14A6QCs9e9baHQu1sHv2wwqYZJt3XgGE-VG73HDFUFagaYQ7U05jIeaYUKPMzbTYSlT3zFpLccbALcd5JpKQr04Jg0hFbyO-NOVSuKiXtLvTN6MN_0qAMGXgjf9JbuRuNMgQ6cZzhIwOETR2dryJycBIx1s7GXbubrZkHh9crIS9I8B4Rq_RXSHk2oIcMyrzyBTnaIPCgTVnIWK8589aQeOlGio3sHcTPery8v4Irn7LRryW_9eW5flAqYEhiXabOZc8wHLWb9AaYGMT10X9uitq2rvwnprco8PiaV-ebuYCyKsYK89hGbyU60eEEsbuF2dCxHIHEDnzC1o9GbmSdUIUf9PdmoNHVm7U_ayTr0kVVPignKFJIjhnFODsF_FzzeDZQudG_owpE6gMw0QsJly6rXLAoA09Nm3wavcPHyKSy_l28LUpJ2XDomyIf6V_MPKZ667MBow4Xd62IcJt_iPN5fHVIkqEkIeud6GtVeTik-5x_cju87BOHmC8tsLRd4UzzX0eJpajys619wVow0HGMvuODMlKcTjrC_wfaSRC5P-F2ICdCWJWfbSRy23Nd1nGP0OPonmhxjn9YolaWrktugztbNHrsibF_bguCnleZ1tqwmiYm5KgPHszxO7k9CIBqSUVsqb5ZeTCznU2QM3m_GeXv_RPZujma-4tEWYmSIGCh3W_FvBhi7Z2-Ba5KhCxRVoN9iI-evNomIcECkb0usU-ZwuWMqrxIDxHTIXxKE3JYPwLTj_n-5Ozolf0gTrwx2aJF6vPSySZlutuPArtOeK9-XSKEdP9D0yNZtzYMjYgv9kzH5b7V3IZWINQkPPO8lo7J8OJNhUYBiiOPT1dXBiIvjhzykyFzmC9t0ydZWU3MjtjfkFHTGxZx0hZxdaKjL5Pec1z52XNYxAyAJebR1FCjwbZjPHB8WhKwm3i0qkDIJbeRC9ODmE-fo62Z9PLEJVxpcBBqUoeB5Qp3loOXT1I0ISrYQXKY17-8ejFAnY3yli4j7FvsTsx5wbNpJ3Lkg-hnjPtz0vUzuFVw894NqQ7C2XIVSXjbER5qC7a2xjgHhOB_wPe9ttzfPQkDLncKzgZ5d3C15xakWcA5rZiWxfDS2pP2Ucud_Gx_taQQr6rfzIDstsYrn7ilDBvSgQXbhLLdwhY-t1-85KDF8pIGB_5MhDxTFSKGfr2lwgqqFi9T2-r5Zzh1_ctews4vFMwsMjFa6YAIqyImicEM60ZH7Ews8LCF1DjxWJ8y5xwGRYz8hoyCyfERRz5A3WFr8ZnOAqbDZUfRw65XI147tuw2G2R0RzlDSZggJ3Sji68daA4lzo5bdJ3A1rljClux_sFQWgACRCaQDDzRJBnDcKrEuJMEwwD-A7q2S3aDKeaw-FR4ybj1HZ_sBLgyvpv3NzShdjHXOZZBnjhCAI-RwEDOobjRDWc6xqQbwTk53h2k9rsvnVOp_s7nJpPJxev3nn_2whxedGecGspAvK9LKvvSX-eMSeJVtrTMF5jxR7b9-NLW-HpxMRIF4CeRCydnZ8.hW-30I7CC3Qbh62zI4paCQ; XFCS=8C5BBC1520874DDF83C5FC145B008BED020C813A5E7777A39C62A5101656F3AA; XFT=AVxPgyj7sTVTpdgHkOF+ttrpDXVmiYGJWX731zQ6zYs=; RT=^\^"z=1^&dm=baidu.com^&si=8b3e0efe-71af-4b80-bbb6-2e9a89ba9543^&ss=m5i97sas^&sl=9^&tt=325^&bcn=https^%^3A^%^2F^%^2Ffclog.baidu.com^%^2Flog^%^2Fweirwood^%^3Ftype^%^3Dperf^&ld=125n^\^"^" ^
  -H ^"Csrf-Token: cc2d08cf7b2c90a2bb66eee84b4451ac^$^$^$1735999389^" ^
  -H ^"Origin: https://aigc.baidu.com^" ^
  -H ^"Referer: https://aigc.baidu.com/make^" ^
  -H ^"Sec-Fetch-Dest: empty^" ^
  -H ^"Sec-Fetch-Mode: cors^" ^
  -H ^"Sec-Fetch-Site: same-origin^" ^
  -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36^" ^
  -H ^"sec-ch-ua: ^\^"Google Chrome^\^";v=^\^"131^\^", ^\^"Chromium^\^";v=^\^"131^\^", ^\^"Not_A Brand^\^";v=^\^"24^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  --data-raw ^"^{^\^"app^\^":^\^"hot_event_recommend^\^",^\^"content^\^":^\^"^李^明^德^控^诉^三^人^行^剧^组^\^",^\^"content_id^\^":^\^"1739955314700495^\^",^\^"hot_info^\^":^{^\^"tab^\^":^\^"^娱^乐^\^",^\^"event_cate^\^":^\^"^娱^乐^\^"^}^}^"

获取热点文案详情:
curl ^"https://aigc.baidu.com/aigc/saas/pc/v1/task/t2t/getDetail?task_id=1735999443261905401^" ^
  -H ^"Accept: */*^" ^
  -H ^"Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7^" ^
  -H ^"Connection: keep-alive^" ^
  -H ^"Cookie: BIDUPSID=0F811928FB4726E22A2E94E3E4B3E50D; PSTM=1657455618; MCITY=-^%^3A; BAIDUID=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; H_WISE_SIDS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; H_WISE_SIDS_BFESS=61027_60853_61390_61393_61388_61430_61444_61470_61495_61518_61528_61359_61608; BAIDUID_BFESS=9B5444DFFEF3D136816041753964041B:SL=0:NR=10:FG=1; ZFY=LmoYTIFAciytvddeaT:BxhGLNdbGk7zNL43UWd0FmuPc:C; __bid_n=194278bf9e6955295fea9b; H_PS_PSSID=61027_60853_61495_61518_61528_61359_61608_61684_61551; BDUSS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BDUSS_BFESS=JiOU9vMS1ITFJ1bDdQVFJCZzBBeks0ZHNtc0FSLXlUUVhCcFQ0dzByemNGcDluRVFBQUFBJCQAAAAAAAAAAAEAAABPCFkf7OHNw8u5u~mkzgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyJd2fciXdnZl; BA_HECTOR=0h052k25a42l0ga40424a5a4bn6h0p1jnfvom1u; hot-current-tab=^%^7B^%^22name^%^22^%^3A^%^22^%^E5^%^A8^%^B1^%^E4^%^B9^%^90^%^22^%^2C^%^22index^%^22^%^3A1^%^7D; XFI=a19182d0-caa4-11ef-a8f1-557631737715; saas-appinfo=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..RnIWZgp-un1Rs05b.qY9EQ8lV7QgElJmXb-NjxvcgYIkf3m0GVGd-r2I1ZpgPEZM6AjSoEPqHGm_S6wgrUcC5XcJGlIoPqQGsl86iNHqP2_cgmD--JpUYH60QR6FgCoE6ezosheIjIgFVEwNFyYh1pRtTn0o_fRj5B5qnFBVSoNd4BkJZ84g0AlYxiS7xCUCi1kva5k4RWruZeYs3dAIOnweCXhHjTy35PMaTwyWHBqJahookRI3VxGY8Y8bZ4w3sFsbLwitBbA48AFm_l2Wyqho3B9eutMqTQCqQnJtaP3FzVAOR0rahc3IZKUtpf9ezWxUqgFkJ4R1EOIHtbZoBXFdlenMyg0TQuSanXXc2uJE4vGU3eqwn40NWGi7kLCRoSFXCx6dcEx2rpngVHJtAY2RLXAnw7zK7jfWRNwO6gO82qbGGPaVZw_TAurrlR14A6QCs9e9baHQu1sHv2wwqYZJt3XgGE-VG73HDFUFagaYQ7U05jIeaYUKPMzbTYSlT3zFpLccbALcd5JpKQr04Jg0hFbyO-NOVSuKiXtLvTN6MN_0qAMGXgjf9JbuRuNMgQ6cZzhIwOETR2dryJycBIx1s7GXbubrZkHh9crIS9I8B4Rq_RXSHk2oIcMyrzyBTnaIPCgTVnIWK8589aQeOlGio3sHcTPery8v4Irn7LRryW_9eW5flAqYEhiXabOZc8wHLWb9AaYGMT10X9uitq2rvwnprco8PiaV-ebuYCyKsYK89hGbyU60eEEsbuF2dCxHIHEDnzC1o9GbmSdUIUf9PdmoNHVm7U_ayTr0kVVPignKFJIjhnFODsF_FzzeDZQudG_owpE6gMw0QsJly6rXLAoA09Nm3wavcPHyKSy_l28LUpJ2XDomyIf6V_MPKZ667MBow4Xd62IcJt_iPN5fHVIkqEkIeud6GtVeTik-5x_cju87BOHmC8tsLRd4UzzX0eJpajys619wVow0HGMvuODMlKcTjrC_wfaSRC5P-F2ICdCWJWfbSRy23Nd1nGP0OPonmhxjn9YolaWrktugztbNHrsibF_bguCnleZ1tqwmiYm5KgPHszxO7k9CIBqSUVsqb5ZeTCznU2QM3m_GeXv_RPZujma-4tEWYmSIGCh3W_FvBhi7Z2-Ba5KhCxRVoN9iI-evNomIcECkb0usU-ZwuWMqrxIDxHTIXxKE3JYPwLTj_n-5Ozolf0gTrwx2aJF6vPSySZlutuPArtOeK9-XSKEdP9D0yNZtzYMjYgv9kzH5b7V3IZWINQkPPO8lo7J8OJNhUYBiiOPT1dXBiIvjhzykyFzmC9t0ydZWU3MjtjfkFHTGxZx0hZxdaKjL5Pec1z52XNYxAyAJebR1FCjwbZjPHB8WhKwm3i0qkDIJbeRC9ODmE-fo62Z9PLEJVxpcBBqUoeB5Qp3loOXT1I0ISrYQXKY17-8ejFAnY3yli4j7FvsTsx5wbNpJ3Lkg-hnjPtz0vUzuFVw894NqQ7C2XIVSXjbER5qC7a2xjgHhOB_wPe9ttzfPQkDLncKzgZ5d3C15xakWcA5rZiWxfDS2pP2Ucud_Gx_taQQr6rfzIDstsYrn7ilDBvSgQXbhLLdwhY-t1-85KDF8pIGB_5MhDxTFSKGfr2lwgqqFi9T2-r5Zzh1_ctews4vFMwsMjFa6YAIqyImicEM60ZH7Ews8LCF1DjxWJ8y5xwGRYz8hoyCyfERRz5A3WFr8ZnOAqbDZUfRw65XI147tuw2G2R0RzlDSZggJ3Sji68daA4lzo5bdJ3A1rljClux_sFQWgACRCaQDDzRJBnDcKrEuJMEwwD-A7q2S3aDKeaw-FR4ybj1HZ_sBLgyvpv3NzShdjHXOZZBnjhCAI-RwEDOobjRDWc6xqQbwTk53h2k9rsvnVOp_s7nJpPJxev3nn_2whxedGecGspAvK9LKvvSX-eMSeJVtrTMF5jxR7b9-NLW-HpxMRIF4CeRCydnZ8.hW-30I7CC3Qbh62zI4paCQ; XFCS=8C5BBC1520874DDF83C5FC145B008BED020C813A5E7777A39C62A5101656F3AA; XFT=AVxPgyj7sTVTpdgHkOF+ttrpDXVmiYGJWX731zQ6zYs=; RT=^\^"z=1^&dm=baidu.com^&si=8b3e0efe-71af-4b80-bbb6-2e9a89ba9543^&ss=m5i97sas^&sl=n^&tt=61x^&bcn=https^%^3A^%^2F^%^2Ffclog.baidu.com^%^2Flog^%^2Fweirwood^%^3Ftype^%^3Dperf^&ld=1e69^\^"^" ^
  -H ^"Referer: https://aigc.baidu.com/make^" ^
  -H ^"Sec-Fetch-Dest: empty^" ^
  -H ^"Sec-Fetch-Mode: cors^" ^
  -H ^"Sec-Fetch-Site: same-origin^" ^
  -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36^" ^
  -H ^"sec-ch-ua: ^\^"Google Chrome^\^";v=^\^"131^\^", ^\^"Chromium^\^";v=^\^"131^\^", ^\^"Not_A Brand^\^";v=^\^"24^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^"


"""