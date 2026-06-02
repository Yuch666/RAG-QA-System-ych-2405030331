"""
任务1：环境搭建与模型部署测试脚本
该脚本用于验证Ollama API是否能正常返回结果

AI生成说明：本脚本由AI辅助生成，用于测试Ollama环境配置
"""

import requests
import json
import sys
from config import OLLAMA_BASE_URL, MODEL_NAME, EMBEDDING_MODEL


def test_ollama_connection():
    """测试Ollama服务连接"""
    print("=" * 50)
    print("测试1：检查Ollama服务连接")
    print("=" * 50)
    
    try:
        response = requests.get(OLLAMA_BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务连接成功！")
            print(f"   服务地址: {OLLAMA_BASE_URL}")
            return True
        else:
            print("❌ Ollama服务连接失败！")
            print(f"   状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务！")
        print("   请确保Ollama已启动（运行命令: ollama serve）")
        return False
    except Exception as e:
        print(f"❌ 连接测试出错: {str(e)}")
        return False


def test_model_list():
    """测试已下载的模型列表"""
    print("\n" + "=" * 50)
    print("测试2：检查已下载的模型")
    print("=" * 50)
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("✅ 已下载的模型列表：")
                for model in models:
                    name = model.get("name", "未知")
                    size = model.get("size", 0)
                    size_gb = size / (1024 * 1024 * 1024)
                    print(f"   - {name} (大小: {size_gb:.2f} GB)")
                
                # 检查目标模型是否存在
                target_models = [MODEL_NAME, "qwen2:7b", EMBEDDING_MODEL]
                found_models = [m["name"] for m in models]
                
                print("\n模型检查结果：")
                for target in target_models:
                    if target in found_models or any(target.split(":")[0] in m for m in found_models):
                        print(f"   ✅ {target} - 已安装")
                    else:
                        print(f"   ⚠️ {target} - 未安装（请运行: ollama pull {target}）")
                
                return True
            else:
                print("⚠️ 暂无已下载的模型")
                print("   请运行以下命令下载模型：")
                print(f"   ollama pull {MODEL_NAME}")
                print(f"   ollama pull {EMBEDDING_MODEL}")
                return False
        else:
            print(f"❌ 获取模型列表失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 模型列表测试出错: {str(e)}")
        return False


def test_model_generation():
    """测试模型生成能力"""
    print("\n" + "=" * 50)
    print("测试3：测试模型生成能力")
    print("=" * 50)
    
    test_prompt = "请用一句话介绍什么是自然语言处理。"
    
    try:
        # 检查是否有可用的模型
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        models = response.json().get("models", [])
        available_models = [m["name"] for m in models]
        
        # 选择可用的模型进行测试
        test_model = None
        for m in available_models:
            if "deepseek" in m.lower() or "qwen" in m.lower():
                test_model = m
                break
        
        if not test_model:
            print("⚠️ 未找到可用的对话模型，跳过生成测试")
            print("   请先下载模型: ollama pull deepseek-r1:7b")
            return False
        
        print(f"使用模型: {test_model}")
        print(f"测试问题: {test_prompt}")
        print("\n正在生成回答...")
        
        payload = {
            "model": test_model,
            "prompt": test_prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "")
            print("✅ 模型生成成功！")
            print(f"\n模型回答:\n{answer[:500]}...")
            return True
        else:
            print(f"❌ 模型生成失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 模型生成超时（可能是模型首次加载，请稍后重试）")
        return False
    except Exception as e:
        print(f"❌ 生成测试出错: {str(e)}")
        return False


def test_embedding_model():
    """测试嵌入模型"""
    print("\n" + "=" * 50)
    print("测试4：测试嵌入模型")
    print("=" * 50)
    
    test_text = "自然语言处理是人工智能的重要分支。"
    
    try:
        # 检查嵌入模型是否可用
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        models = response.json().get("models", [])
        available_models = [m["name"] for m in models]
        
        # 选择可用的嵌入模型
        embed_model = None
        for m in available_models:
            if "nomic" in m.lower() or "minilm" in m.lower() or "embed" in m.lower():
                embed_model = m
                break
        
        if not embed_model:
            print("⚠️ 未找到嵌入模型，跳过嵌入测试")
            print(f"   请先下载嵌入模型: ollama pull {EMBEDDING_MODEL}")
            return False
        
        print(f"使用嵌入模型: {embed_model}")
        print(f"测试文本: {test_text}")
        print("\n正在生成嵌入向量...")
        
        payload = {
            "model": embed_model,
            "prompt": test_text
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print("✅ 嵌入模型工作正常！")
            print(f"   向量维度: {len(embedding)}")
            print(f"   向量示例（前5个值）: {embedding[:5]}")
            return True
        else:
            print(f"❌ 嵌入生成失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 嵌入测试出错: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("    RAG智能问答系统 - 环境配置测试")
    print("=" * 60)
    print(f"\n配置信息：")
    print(f"  Ollama地址: {OLLAMA_BASE_URL}")
    print(f"  对话模型: {MODEL_NAME}")
    print(f"  嵌入模型: {EMBEDDING_MODEL}")
    print("\n")
    
    results = []
    
    # 运行各项测试
    results.append(("Ollama连接", test_ollama_connection()))
    results.append(("模型列表", test_model_list()))
    results.append(("模型生成", test_model_generation()))
    results.append(("嵌入模型", test_embedding_model()))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("    测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！环境配置完成，可以开始使用RAG系统。")
        return 0
    else:
        print("\n⚠️ 部分测试未通过，请检查上述提示并完成相应配置。")
        print("\n常见解决方案：")
        print("  1. 启动Ollama服务: ollama serve")
        print(f"  2. 下载对话模型: ollama pull {MODEL_NAME}")
        print(f"  3. 下载嵌入模型: ollama pull {EMBEDDING_MODEL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())