#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成JMeter测试计划脚本（优化版）
- 保留接口中文名称
- 自动转义XML特殊字符
- 提取Postman断言内容
- 完善Header处理
- 详细注释关键逻辑
"""

import json
import os
import html
from datetime import datetime

# JMeter测试计划模板
JMETER_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="KunLun API Test" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="server_url" elementType="Argument">
            <stringProp name="Argument.name">server_url</stringProp>
            <stringProp name="Argument.value">{server_url}</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="API Test Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">100</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">10</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        {http_samplers}
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
        <ResultCollector guiclass="StatVisualizer" testclass="ResultCollector" testname="Aggregate Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
'''

# HTTP请求采样器模板
HTTP_SAMPLER_TEMPLATE = '''
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="API_{index}" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="HTTPSampler.domain">${{server_url}}</stringProp>
  <stringProp name="HTTPSampler.port"></stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.path">{path}</stringProp>
  <stringProp name="HTTPSampler.method">{method}</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
  <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
  <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">false</boolProp>
  <boolProp name="HTTPSampler.image_parser">false</boolProp>
  <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
  <boolProp name="HTTPSampler.md5">false</boolProp>
  <intProp name="HTTPSampler.ipSourceType">0</intProp>
</HTTPSamplerProxy>
<hashTree>
  <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
    <collectionProp name="HeaderManager.headers">
      <elementProp name="" elementType="Header">
        <stringProp name="Header.name">Authorization</stringProp>
        <stringProp name="Header.value">${{token}}</stringProp>
      </elementProp>
      <elementProp name="" elementType="Header">
        <stringProp name="Header.name">Accept</stringProp>
        <stringProp name="Header.value">*/*</stringProp>
      </elementProp>
    </collectionProp>
  </HeaderManager>
  <hashTree/>
  <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion" enabled="true">
    <collectionProp name="Asserion.test_strings">
      <stringProp name="49586">200</stringProp>
    </collectionProp>
    <stringProp name="Assertion.custom_message"></stringProp>
    <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
    <boolProp name="Assertion.assume_success">false</boolProp>
    <intProp name="Assertion.test_type">8</intProp>
  </ResponseAssertion>
  <hashTree/>
</hashTree>
'''

def xml_escape(text):
    """转义XML特殊字符，保留中文"""
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text, quote=True)

def load_config():
    """加载配置文件"""
    config_path = os.path.join('src', 'tools', 'jmeter', 'project_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_postman_collection():
    """加载Postman Collection"""
    collection_path = os.path.join('src', 'tools', 'jmeter', '昆仑卫士.postman_collection.json')
    with open(collection_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_requests(items, parent_name=""):
    """
    递归提取Postman Collection中的所有请求，保留分组和中文名称
    返回格式：[{name, method, path, headers, asserts}]
    """
    requests = []
    for item in items:
        group = parent_name + "/" + item['name'] if parent_name else item['name']
        if 'request' in item:
            # 提取断言
            asserts = []
            if 'event' in item:
                for ev in item['event']:
                    if ev.get('listen') == 'test' and 'script' in ev and 'exec' in ev['script']:
                        for line in ev['script']['exec']:
                            if 'to.equal(200)' in line or 'to.equal(\'200\')' in line:
                                asserts.append('200')
            # 提取header
            headers = []
            for h in item['request'].get('header', []):
                if not h.get('disabled') and h.get('key'):
                    headers.append((h['key'], h['value']))
            # 提取路径
            path = '/' + '/'.join(item['request']['url']['path'])
            requests.append({
                'name': group,
                'method': item['request']['method'],
                'path': path,
                'headers': headers,
                'asserts': asserts
            })
        if 'item' in item:
            requests.extend(extract_requests(item['item'], group))
    return requests

def build_header_manager(headers):
    """生成JMeter HeaderManager XML片段"""
    xml_lines = [
        '<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">',
        '  <collectionProp name="HeaderManager.headers">'
    ]
    for k, v in headers:
        xml_lines.append('    <elementProp name="" elementType="Header">')
        xml_lines.append(f'      <stringProp name="Header.name">{xml_escape(k)}</stringProp>')
        xml_lines.append(f'      <stringProp name="Header.value">{xml_escape(v)}</stringProp>')
        xml_lines.append('    </elementProp>')
    xml_lines.append('  </collectionProp>')
    xml_lines.append('</HeaderManager>')
    xml_lines.append('<hashTree/>')
    return '\n'.join(xml_lines)

def build_assertion(asserts):
    """生成JMeter响应断言XML片段"""
    if not asserts:
        return ''
    xml_lines = [
        '<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言" enabled="true">',
        '  <collectionProp name="Asserion.test_strings">'
    ]
    for a in asserts:
        xml_lines.append(f'    <stringProp name="49586">{xml_escape(a)}</stringProp>')
    xml_lines.append('  </collectionProp>')
    xml_lines.append('  <stringProp name="Assertion.custom_message"></stringProp>')
    xml_lines.append('  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>')
    xml_lines.append('  <boolProp name="Assertion.assume_success">false</boolProp>')
    xml_lines.append('  <intProp name="Assertion.test_type">8</intProp>')
    xml_lines.append('</ResponseAssertion>')
    xml_lines.append('<hashTree/>')
    return '\n'.join(xml_lines)

def build_http_sampler(req):
    """生成JMeter HTTP采样器XML片段，保留中文名称"""
    sampler = f'''
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{xml_escape(req['name'])}" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="HTTPSampler.domain">${{server_url}}</stringProp>
  <stringProp name="HTTPSampler.port"></stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.path">{xml_escape(req['path'])}</stringProp>
  <stringProp name="HTTPSampler.method">{xml_escape(req['method'])}</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
  <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
  <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">false</boolProp>
  <boolProp name="HTTPSampler.image_parser">false</boolProp>
  <boolProp name="HTTPSampler.concurrentDwn">false</boolProp>
  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
  <boolProp name="HTTPSampler.md5">false</boolProp>
  <intProp name="HTTPSampler.ipSourceType">0</intProp>
</HTTPSamplerProxy>
<hashTree>
{build_header_manager(req['headers'])}
{build_assertion(req['asserts'])}
</hashTree>
'''
    return sampler

def generate_jmx():
    """生成JMeter测试计划"""
    config = load_config()
    collection = load_postman_collection()
    
    # 提取所有请求
    requests = extract_requests(collection['item'])
    
    # 生成HTTP采样器
    http_samplers = ''
    for req in requests:
        http_samplers += build_http_sampler(req)
    
    # 生成完整的JMeter测试计划
    jmx_content = JMETER_TEMPLATE.format(
        server_url=xml_escape(config['server_url']),
        http_samplers=http_samplers
    )
    
    # 保存JMX文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    jmx_path = os.path.join('src', 'tools', 'jmeter', f'kunlun_test_{timestamp}.jmx')
    with open(jmx_path, 'w', encoding='utf-8') as f:
        f.write(jmx_content)
    
    return jmx_path

def main():
    """主函数"""
    try:
        jmx_path = generate_jmx()
        print(f'JMeter测试计划已生成：{jmx_path}')
        print('\n使用以下命令运行测试：')
        print(f'src\\tools\\jmeter\\bin\\jmeter.bat -n -t {jmx_path} -l result.jtl')
        
        # 生成HTML报告的命令
        report_path = os.path.join('src', 'tools', 'jmeter', 'report')
        print('\n生成HTML报告：')
        print(f'src\\tools\\jmeter\\bin\\jmeter.bat -n -t {jmx_path} -l result.jtl -e -o {report_path}')
        
    except Exception as e:
        print(f'错误：{str(e)}')

if __name__ == '__main__':
    main() 