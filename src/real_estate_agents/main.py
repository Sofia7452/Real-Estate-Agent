import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.real_estate_agents.multi_agent_system import RealEstateMultiAgentSystem

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    房地产推荐多智能体系统主程序
    """
    print("\n" + "="*50)
    print("欢迎使用房地产推荐系统！")
    print("="*50)
    print("\n本系统使用多智能体架构，包含三个智能体：")
    print("1. 需求Agent - 解析您的自然语言需求")
    print("2. 房源Agent - 搜索符合条件的房源")
    print("3. 匹配推荐Agent - 根据匹配度推荐最佳房源")
    print("\n请描述您的购房需求 (如预算、区域、学区、通勤等):")
    print("例如：'我想在朝阳区买一套300-500万的房子，最好是朝阳实验小学的学区房，通勤时间不超过30分钟'")
    print("="*50 + "\n")
    
    # 初始化多智能体系统
    try:
        multi_agent_system = RealEstateMultiAgentSystem()
        logger.info("多智能体系统初始化成功")
    except Exception as e:
        logger.error(f"初始化多智能体系统失败: {e}")
        print(f"系统初始化失败: {e}")
        return
    
    while True:
        user_input = input("\n请输入您的需求 (输入'退出'结束): ")
        
        if user_input.lower() in ["退出", "exit", "quit", "q"]:
            print("\n感谢使用房地产推荐系统！")
            break
        
        # 调用多智能体系统处理查询
        try:
            print("\n正在处理您的需求，请稍候...\n")
            response = multi_agent_system.process_user_query(user_input)
            
            # 打印推荐结果
            recommendations = response.get("recommendations", [])
            if recommendations:
                print("\n" + "="*50)
                print(f"为您找到 {len(recommendations)} 个匹配的房源:")
                print("="*50)
                
                for rec in recommendations:
                    property_info = rec.get("property_info", {})
                    score = rec.get("score_breakdown", {})
                    
                    print(f"\n【{rec.get('rank', 0)}】{property_info.get('address')} ({property_info.get('area')})")
                    print(f"  价格: ¥{property_info.get('price', 0):,}")
                    print(f"  房型: {property_info.get('bedrooms', 0)}室{property_info.get('bathrooms', 0)}卫 ({property_info.get('size', 0)}平米)")
                    print(f"  学区: {property_info.get('school_district', '未知')}")
                    print(f"  通勤时间: {property_info.get('commute_time', 0)}分钟")
                    print(f"  匹配度: {rec.get('matching_score', 0)*100:.1f}%")
                    print(f"  推荐理由: {rec.get('reason', '')}")
                    print(f"  匹配详情:")
                    print(f"    - 预算匹配: {score.get('budget', 0)*100:.1f}%")
                    print(f"    - 区域匹配: {score.get('area', 0)*100:.1f}%")
                    print(f"    - 学区匹配: {score.get('school', 0)*100:.1f}%")
                    print(f"    - 通勤匹配: {score.get('commute', 0)*100:.1f}%")
                
                print("\n" + "="*50)
                print("推荐总结:")
                print(f"  价格范围: ¥{response.get('price_range', {}).get('min', 0):,} - ¥{response.get('price_range', {}).get('max', 0):,}")
                print(f"  平均匹配度: {response.get('average_matching_score', 0)*100:.1f}%")
                print("="*50)
            else:
                print("\n未找到符合您要求的房源，请尝试调整您的需求。")
                
        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            print(f"处理您的请求时出现问题: {str(e)}")

if __name__ == "__main__":
    main()
