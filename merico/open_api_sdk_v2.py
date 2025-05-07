# Account

# 以Account聚合获取效率指标
# http://demo.meri.co/openapi/account/query-efficiency-metric
def get_efficiency_metric_by_account_id(client, selectAccountIds, start_date, end_date, unitOfTime, testCode):
    data = {}
    data["options"] = {}
    if selectAccountIds:
        data["accountIds"] = selectAccountIds
    if start_date or end_date:
        data["options"]['authorTime'] = {}
        data["options"]['authorTime']['startDate'] = start_date
        data["options"]['authorTime']['endDate'] = end_date
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode == True or testCode == False:
        data["options"]['testCode'] = testCode

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('commit_num')                     # 提交数
    data["options"]['selectColumns'].append('function_num')                   # 函数个数
    data["options"]['selectColumns'].append('loc')                            # 代码行数
    data["options"]['selectColumns'].append('loc_add_line')                   # 新增代码行数
    data["options"]['selectColumns'].append('loc_delete_line')                # 删除代码行数
    data["options"]['selectColumns'].append('share_loc')                      # 代码行数占比
    data["options"]['selectColumns'].append('developer_num')                  # 开发者人数
    data["options"]['selectColumns'].append('dev_equivalent')                 # 开发当量
    data["options"]['selectColumns'].append('dev_value')                      # 开发价值
    data["options"]['selectColumns'].append('dev_value_robustness')           # 开发价值鲁棒性（开发者开发价值贡献是否均衡）
    data["options"]['selectColumns'].append('dev_equivalent_every_developer') # 开发者平均开发当量
    # 代码行数在查询测试/非测试代码（包含testCode参数），或过滤文件路径（包含projectFolderFilter参数）时，
    # 行数计算是基于函数修改前后文本的对比，不是直接从git commit diff获取的原始增删行数，与commit粒度的查询结果会存在差异。
    code, message, result = client.request('/account/query-efficiency-metric', data)

    assert code == 200, message
    return result


# 以Account聚合获取质量指标
# http://demo.meri.co/openapi/account/query-quality-metric
def get_quality_metric_by_account_id(client, selectAccountIds):
    data = {}
    data["options"] = {}
    if selectAccountIds:
        data["accountIds"] = selectAccountIds

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('doc_coverage_function_num')                 # 有注释覆盖的函数个数
    data["options"]['selectColumns'].append('doc_coverage_total_function_num')           # 计算注释覆盖度的总函数个数（包含所有函数）
    data["options"]['selectColumns'].append('doc_coverage')                              # 注释覆盖度
    data["options"]['selectColumns'].append('static_test_coverage_function_num')         # 有测试覆盖的函数个数
    data["options"]['selectColumns'].append('static_test_coverage_total_function_num')   # 计算测试覆盖度的总函数个数（不包含匿名函数和测试函数的函数个数）
    data["options"]['selectColumns'].append('static_test_coverage')                      # 测试覆盖度

    data["options"]['selectColumns'].append('issue_blocker_num')                         # 阻塞问题数
    data["options"]['selectColumns'].append('issue_critical_num')                        # 严重问题数
    data["options"]['selectColumns'].append('issue_info_num')                            # 提醒问题数
    data["options"]['selectColumns'].append('issue_major_num')                           # 重要问题数
    data["options"]['selectColumns'].append('issue_minor_num')                           # 次要问题数
    data["options"]['selectColumns'].append('issue_num')                                 # 总代码问题数

    data["options"]['selectColumns'].append('issue_rate')                                # 代码问题比例（函数占比）
    data["options"]['selectColumns'].append('severe_issue_rate')                         # 重要问题密度: (issue_blocker_count + issue_critical_count) / total_dev_eq
    data["options"]['selectColumns'].append('weighted_issue_rate')                       # 加权问题数比例（函数占比）

    data["options"]['selectColumns'].append('function_depend')                           # 开发者影响力
    data["options"]['selectColumns'].append('ccg_snapshot_function_num')                 # 分析切面总函数个数
    data["options"]['selectColumns'].append('duplicate_function_num')                    # 重复函数个数
    data["options"]['selectColumns'].append('dryness')                                   # 代码不重复率
    data["options"]['selectColumns'].append('modularity')                                # 代码模块度
    data["options"]['selectColumns'].append('cyclomatic_total')                          # 全函数圈复杂度之和
    data["options"]['selectColumns'].append('cyclomatic_total_every_function')           # 平均每个函数圈复杂度
    data["options"]['selectColumns'].append('cyclomatic_total_every_1k_dev_eq')          # 平均每个千当量圈复杂度

    data["options"]['selectColumns'].append('techtag')                                   # 技能tag标签

    code, message, result = client.request('/account/query-quality-metric', data)

    assert code == 200, message
    return result


# 查询账户列表
# http://demo.meri.co/openapi/account/list
def get_account_list(client):
    code, message, result = client.request('/account/list', {})
    assert code == 200, message
    return result



# 查询账户信息
# http://demo.meri.co/openapi/account/query
def get_account_info_by_email(client, accountId):
    code, message, result = client.request('/account/query', {
        "id": accountId,
    })
    assert code == 200, message
    return result



# 添加账户
# http://demo.meri.co/openapi/account/add
def account_add(client, account_add_dict):
    # print(f"account_add_dict = {account_add_dict}")
    data = {}
    data["name"] = account_add_dict["姓名"]
    data["email"] = account_add_dict["用户主邮箱地址"]
    if account_add_dict["工号"]: 
        data["jobNumber"] = account_add_dict["工号"]
    else:
        None
    if account_add_dict["职位"]: 
        data["title"] = account_add_dict["职位"]
    else:
        None
    if account_add_dict["薪资"]:
        data["salary"] = account_add_dict["薪资"]
    else:
        None
    if account_add_dict["职级"]:
        data["rank"] = account_add_dict["职级"]
    else:
        None
    if account_add_dict["晋升日期"]:
        data["promotionDate"] = account_add_dict["晋升日期"]
    else:
        None
    if account_add_dict["所属团队ID列表"]:
        data["teamIds"] = account_add_dict["所属团队ID列表"].split(',')
    else:
        None
    if account_add_dict["用户角色ID列表"]:
        data["roleIds"] = account_add_dict["用户角色ID列表"].split(',')
    else:
        None
    if account_add_dict["项目ID列表"]:
        data["projectIds"] = account_add_dict["项目ID列表"].split(',')
    else:
        None
    code, message, result = client.request('/account/add', data)

    return code, message, result



# 更新账户
# http://demo.meri.co/openapi/account/update
def account_update(client, account_update_dict):
    # print(f"account_update_dict = {account_update_dict}")
    data = {}
    data["id"] = account_update_dict["账户ID"]
    if account_update_dict["姓名"]:
        data["name"] = account_update_dict["姓名"]
    else:
        None
    if account_update_dict["用户副邮箱地址"]:
        data["emails"] = account_update_dict["用户副邮箱地址"]
    else:
        None
    if account_update_dict["自定义标签"]:
        data["tags"] = account_update_dict["自定义标签"]
    else:
        None
    if account_update_dict["工号"]:
        data["jobNumber"] = account_update_dict["工号"]
    else:
        None
    if account_update_dict["职位"]:
        data["title"] = account_update_dict["职位"]
    else:
        None
    if account_update_dict["薪资"]:
        data["salary"] = account_update_dict["薪资"]
    else:
        None
    if account_update_dict["职级"]:
        data["rank"] = account_update_dict["职级"]
    else:
        None
    if account_update_dict["晋升日期"]:
        data["promotionDate"] = account_update_dict["晋升日期"]
    else:
        None
    if account_update_dict["所属团队ID列表"]:
        data["teamIds"] = account_update_dict["所属团队ID列表"].split(',')
    else:
        None
    if account_update_dict["用户角色ID列表"]:
        data["roleIds"] = account_update_dict["用户角色ID列表"].split(',')
    else:
        None
    if account_update_dict["项目ID列表"]:
        data["projectIds"] = account_update_dict["项目ID列表"].split(',')
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update', data)

    return code, message, result



# 删除账户
# http://demo.meri.co/openapi/account/delete
def account_delete(client, account_delete_dict):
    # print(f"account_delete_dict = {account_delete_dict}")
    data = {}
    data["id"] = account_delete_dict["账户ID"]
    # print(f"data = {data}")
    code, message, result = client.request('/account/delete', data)

    return code, message, result



# 更新账户状态（启用/禁用，登陆/非登陆）
# http://demo.meri.co/openapi/account/update-status
def account_update_status(client, account_update_dict):
    # print(f"account_update_dict = {account_update_dict}")
    data = {}
    data["id"] = account_update_dict["账户ID"]
    if account_update_dict["用户账户是否启用"]:
        data["enable"] = account_update_dict["用户账户是否启用"]
    else:
        None
    if account_update_dict["用户账户是否可登录"]:
        data["allowLogin"] = account_update_dict["用户账户是否可登录"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update-status', data)

    return code, message, result



# 添加账户代码仓库权限
# http://demo.meri.co/openapi/account/add-repos
def account_add_repos(client, account_add_repos):
    # print(f"account_add_repos = {account_add_repos}")
    data = {}
    data["id"] = account_add_repos["账户ID"]
    if account_add_repos["代码仓库ID列表"] or account_add_repos["代码仓库ID列表"] == []:
        data["repoIds"] = account_add_repos["代码仓库ID列表"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/add-repos', data)

    return code, message, result




# 删除账户代码仓库权限
# http://demo.meri.co/openapi/account/remove-repos
def account_remove_repos(client, account_remove_repos):
    # print(f"account_remove_repos = {account_remove_repos}")
    data = {}
    data["id"] = account_remove_repos["账户ID"]
    if account_remove_repos["代码仓库ID列表"] or account_remove_repos["代码仓库ID列表"] == []:
        data["repoIds"] = account_remove_repos["代码仓库ID列表"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/remove-repos', data)

    return code, message, result


# 更新（覆盖）账户的代码仓库权限
# http://demo.meri.co/openapi/account/update-repos
def account_update_repos(client, account_update_repos):
    # print(f"account_update_repos = {account_update_repos}")
    data = {}
    data["id"] = account_update_repos["账户ID"]
    if account_update_repos["代码仓库ID列表"] or account_update_repos["代码仓库ID列表"] == []:
        data["repoIds"] = account_update_repos["代码仓库ID列表"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update-repos', data)

    return code, message, result


# 更新（覆盖）账户的团队权限
# http://demo.meri.co/openapi/account/update-teams
def account_update_teams(client, account_update_teams):
    # print(f"account_update_teams = {account_update_teams}")
    data = {}
    data["id"] = account_update_teams["账户ID"]
    if account_update_teams["团队ID列表"] or account_update_teams["团队ID列表"] == []:
        data["teamIds"] = account_update_teams["团队ID列表"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update-teams', data)

    return code, message, result


# 更新（覆盖）账户的项目权限
# http://demo.meri.co/openapi/account/update-projectss
def account_update_projects(client, account_update_projects):
    # print(f"account_update_projects = {account_update_projects}")
    data = {}
    data["id"] = account_update_projects["账户ID"]
    if account_update_projects["项目ID列表"] or account_update_projects["项目ID列表"] == []:
        data["projectIds"] = account_update_projects["项目ID列表"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update-projects', data)

    return code, message, result


# 将用户密码重置为随机字符串并返回
# http://demo.meri.co/openapi/account/reset-password
def account_reset_password(client, account_reset_password):
    # print(f"account_reset_password = {account_reset_password}")
    data = {}
    data["id"] = account_reset_password["账户ID"]
    # print(f"data = {data}")
    code, message, result = client.request('/account/reset-password', data)

    return code, message, result


# 更新用户主邮箱
# http://demo.meri.co/openapi/docs#tag/Account/paths/~1account~1update-email/post
def account_update_email(client, account_update_email):
    # print(f"account_update_email = {account_update_email}")
    data = {}
    data["id"] = account_update_email["账户ID"]
    if account_update_email["用户主邮箱"]:
        data["email"] = account_update_email["用户主邮箱"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/account/update-email', data)

    return code, message, result



# 获取用户团队信息历史
# http://demo.meri.co/openapi/account/batch-query-team-history
def get_account_batch_query_team_history(client, accountEmails):
    # print(f"accountEmails = {accountEmails}")
    data = {}
    data["accountEmails"] = accountEmails
    # print(f"data = {data}")
    code, message, result = client.request('/account/batch-query-team-history', data)

    return code, message, result




# 批量添加用户到团队
# http://demo.meri.co/openapi/account/batch-reset-team
def account_batch_reset_team(client, account_batch_reset_team):
    # print(f"account_batch_reset_team = {account_batch_reset_team}")
    data = {}
    data["items"] = account_batch_reset_team
    # print(f"data = {data}")
    code, message, result = client.request('/account/batch-reset-team', data)

    return code, message, result



# 将提交作者emails加入黑名单
# http://demo.meri.co/openapi/account/account/exclude-commit-author
def account_exclude_commit_author(client, account_exclude_commit_author):
    # print(f"account_exclude_commit_author = {account_exclude_commit_author}")
    data = {}
    data["emails"] = account_exclude_commit_author
    # print(f"data = {data}")
    code, message, result = client.request('/account/exclude-commit-author', data)

    return code, message, result



# 将提交作者emails移出黑名单
# http://demo.meri.co/openapi/account/account/include-commit-author
def account_include_commit_author(client, account_include_commit_author):
    # print(f"account_include_commit_author = {account_include_commit_author}")
    data = {}
    data["emails"] = account_include_commit_author
    # print(f"data = {data}")
    code, message, result = client.request('/account/include-commit-author', data)

    return code, message, result



# Repo
# http://demo.meri.co/openapi/repo/add
# 创建代码库
def repo_add(client, repo_add_dict):
    # print(f"repo_add_dict = {repo_add_dict}")
    data = {}
    data["gitUrl"] = repo_add_dict["gitUrl"]
    if repo_add_dict["privateKey"]:
        data["privateKey"] = repo_add_dict["privateKey"]
    if repo_add_dict["username"]:
        data["username"] = repo_add_dict["username"]
    if repo_add_dict["password"]:
        data["password"] = repo_add_dict["password"]
    if repo_add_dict["defaultRef"]:
        data["defaultRef"] = repo_add_dict["defaultRef"]
    if repo_add_dict["projectId"]:
        data["projectId"] = repo_add_dict["projectId"]
    # print(f"data = {data}")
    code, message, result = client.request('/repo/add', data)

    return code, message, result



# 删除代码库，V2接口
def repo_delete(client, repo_delete_dict):
    # print(f"repo_delete_dict = {repo_delete_dict}")
    data = {}
    data["id"] = repo_delete_dict["代码库ID"]
    # print(f"data = {data}")
    code, message, result = client.request('/repo/delete', data)

    return code, message, result


# 以代码库聚合获取效率metric
# http://demo.meri.co/openapi/repo/query-efficiency-metric
def get_efficiency_metric_by_repo_id(client, selectRepoIds, start_date, end_date, unitOfTime, testCode):
    data = {}
    data["options"] = {}
    if selectRepoIds:
        if type(selectRepoIds) == str:
            data["repoIds"] = [selectRepoIds]
        if type(selectRepoIds) == list:
            data["repoIds"] = selectRepoIds
    if start_date or end_date:
        data["options"]['authorTime'] = {}
        data["options"]['authorTime']['startDate'] = start_date
        data["options"]['authorTime']['endDate'] = end_date
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode == True or testCode == False:
        data["options"]['testCode'] = testCode

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('commit_num')                     # 提交数
    data["options"]['selectColumns'].append('function_num')                   # 函数个数
    data["options"]['selectColumns'].append('loc')                            # 代码行数
    data["options"]['selectColumns'].append('loc_add_line')                   # 新增代码行数
    data["options"]['selectColumns'].append('loc_delete_line')                # 删除代码行数
    data["options"]['selectColumns'].append('share_loc')                      # 代码行数占比
    data["options"]['selectColumns'].append('developer_num')                  # 开发者人数
    data["options"]['selectColumns'].append('dev_equivalent')                 # 开发当量
    data["options"]['selectColumns'].append('dev_value')                      # 开发价值
    data["options"]['selectColumns'].append('dev_value_robustness')           # 开发价值鲁棒性（开发者开发价值贡献是否均衡）
    data["options"]['selectColumns'].append('dev_equivalent_every_developer') # 开发者平均开发当量
    # 代码行数在查询测试/非测试代码（包含testCode参数），或过滤文件路径（包含projectFolderFilter参数）时，
    # 行数计算是基于函数修改前后文本的对比，不是直接从git commit diff获取的原始增删行数，与commit粒度的查询结果会存在差异。
    code, message, result = client.request('/repo/query-efficiency-metric', data)

    assert code == 200, message
    return result


# 以代码库聚合获取质量metric
# http://demo.meri.co/openapi/repo/query-qualisy-metric
def get_quality_metric_by_repo_id(client, selectRepoIds):
    data = {}
    data["options"] = {}
    if selectRepoIds:
        if type(selectRepoIds) == str:
            data["repoIds"] = [selectRepoIds]
        if type(selectRepoIds) == list:
            data["repoIds"] = selectRepoIds

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('doc_coverage_function_num')              # 有注释覆盖的函数个数
    data["options"]['selectColumns'].append('doc_coverage_total_function_num')        # 计算注释覆盖度的总函数个数（包含所有函数）
    data["options"]['selectColumns'].append('doc_coverage')                           # 注释覆盖度
    data["options"]['selectColumns'].append('static_test_coverage_function_num')      # 有测试覆盖的函数个数
    data["options"]['selectColumns'].append('static_test_coverage_total_function_num')# 计算测试覆盖度的总函数个数（不包含匿名函数和测试函数的函数个数）
    data["options"]['selectColumns'].append('static_test_coverage')                   # 测试覆盖度

    data["options"]['selectColumns'].append('issue_blocker_num')                      # 阻塞问题数
    data["options"]['selectColumns'].append('issue_critical_num')                     # 严重问题数
    data["options"]['selectColumns'].append('issue_info_num')                         # 提醒问题数
    data["options"]['selectColumns'].append('issue_major_num')                        # 重要问题数
    data["options"]['selectColumns'].append('issue_minor_num')                        # 次要问题数
    data["options"]['selectColumns'].append('issue_num')                              # 总代码问题数

    data["options"]['selectColumns'].append('issue_rate')                             # 代码问题比例（函数占比）
    data["options"]['selectColumns'].append('severe_issue_rate')                      # 重要问题密度: (issue_blocker_count + issue_critical_count) / total_dev_eq
    data["options"]['selectColumns'].append('weighted_issue_rate')                    # 加权问题数比例（函数占比）

    data["options"]['selectColumns'].append('function_depend')                        # 开发者影响力
    data["options"]['selectColumns'].append('ccg_snapshot_function_num')              # 分析切面总函数个数
    data["options"]['selectColumns'].append('duplicate_function_num')                 # 重复函数个数
    data["options"]['selectColumns'].append('dryness')                                # 代码不重复率
    data["options"]['selectColumns'].append('modularity')                             # 代码模块度
    data["options"]['selectColumns'].append('cyclomatic_total')                       # 全函数圈复杂度之和
    data["options"]['selectColumns'].append('cyclomatic_total_every_function')        # 平均每个函数圈复杂度
    data["options"]['selectColumns'].append('cyclomatic_total_every_1k_dev_eq')       # 平均每个千当量圈复杂度

    data["options"]['selectColumns'].append('techtag')                                # 技能tag标签

    code, message, result = client.request('/repo/query-quality-metric', data)

    assert code == 200, message
    return result


# 查询代码质量问题
# http://demo.meri.co/openapi/repo/list-issues
def get_repo_list_issues(client, RepoId, page_size):
    final_result = {}
    result = [1]
    page = 1
    while len(result) != 0:
        code, message, result = client.request('/repo/list-issues', {
            "id": RepoId,
            "page": page,
            "pagesize": page_size
            })
        assert code == 200, message
        if len(result) != 0:
            for i in result:
                final_result[f"{i['id']}-{i['ruleKey']}-{i['hash']}"] = i
            # print(f"获取到最新的 {page} 页面数据 数量为 {len(result)}")
        page += 1
    print(f"代码库ID: {RepoId} 获取到的思码逸内代码质量问题数量是 {len(final_result)} ")

    return final_result


# 获取所有代码库信息，V2接口
def get_all_repo_id(client):
    code, message, result = client.request('/repo/list', {})
    assert code == 200, message
    return result


# 获取所有代码库dict，V2接口
def get_all_repo_dict(client):
    repo_list = get_all_repo_id(client)
    repo_dict = {repo['id']: repo for repo in repo_list}
    return repo_dict


# 查询已经添加的代码库，V2接口
def query_repo_by_id(client, RepoId):
    code, message, result = client.request('/repo/query', {
        "id": RepoId,
        })
    assert code == 200, message
    return result







# 查询代码库指定分析的代码分支列表(目前配置分析参数中代码当量分析的分支)
# http://demo.meri.co/openapi/repo/analyzed_branches
def get_repo_analyzed_branches(client, repoIds):
    data = {}
    if repoIds:
        if type(repoIds) == str:
            data["repoIds"] = [repoIds]
        if type(repoIds) == list:
            data["repoIds"] = repoIds
    code, message, result = client.request('/repo/analyzed_branches', data)
    return code, message, result



# 查询代码库远程分支和Tag列表
# http://demo.meri.co/openapi/repo/ls-remote
def get_repo_ls_remote(client, repoId):
    data = {}
    if repoId:
        data["id"] = repoId
    code, message, result = client.request('/repo/ls-remote', data)
    return code, message, result


# 按分支汇总查询代码库的效率指标(branches选择范围为分析设置中选择了的分析分支)
# http://demo.meri.co/openapi/repo/query-efficiency-by-branch
def query_efficiency_by_branch(client, repoId, branches, startDate, endDate, unitOfTime):
    data = {}
    if repoId:
        data["repoId"] = repoId
    if branches:
        if type(branches) == str:
            data["branches"] = [branches]
        elif type(branches) == list:
            data["branches"] = branches
        else:
            pass
    if startDate:
        data["startDate"] = startDate
    if endDate:
        data["endDate"] = endDate
    if unitOfTime:
        data["unitOfTime"] = unitOfTime
    code, message, result = client.request('/repo/query-efficiency-by-branch', data)
    return code, message, result



# 通过git rev-list筛选commit-hash列表，获取效率metric---获取代码库指定分析分支的效率
# http://demo.meri.co/openapi/repo/hash/query-efficiency-metric
def repo_hash_query_efficiency_metric_by_branch(client, repo_id, single_branch, startDate, endDate, unitOfTime, testCode, developer_name_list):
    data = {}
    data["options"] = {}
    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('commit_num')                     # 提交数
    data["options"]['selectColumns'].append('function_num')                   # 函数个数
    data["options"]['selectColumns'].append('loc')                            # 代码行数
    data["options"]['selectColumns'].append('loc_add_line')                   # 新增代码行数
    data["options"]['selectColumns'].append('loc_delete_line')                # 删除代码行数
    data["options"]['selectColumns'].append('share_loc')                      # 代码行数占比
    data["options"]['selectColumns'].append('developer_num')                  # 开发者人数
    data["options"]['selectColumns'].append('dev_equivalent')                 # 开发当量
    data["options"]['selectColumns'].append('dev_value')                      # 开发价值
    data["options"]['selectColumns'].append('dev_value_robustness')           # 开发价值鲁棒性（开发者开发价值贡献是否均衡）
    data["options"]['selectColumns'].append('dev_equivalent_every_developer') # 开发者平均开发当量
    # 代码行数在查询测试/非测试代码（包含testCode参数），或过滤文件路径（包含projectFolderFilter参数）时，
    # 行数计算是基于函数修改前后文本的对比，不是直接从git commit diff获取的原始增删行数，与commit粒度的查询结果会存在差异。
    if repo_id:
        data["repoRevMap"] = {}
        data["repoRevMap"][repo_id] = {}
        if single_branch:
            data["repoRevMap"][repo_id]['revList'] = [single_branch]
        if startDate:
            data["repoRevMap"][repo_id]['since'] = startDate
        if endDate:
            data["repoRevMap"][repo_id]['until'] = endDate
        if developer_name_list:
            data["repoRevMap"][repo_id]['authors'] = developer_name_list
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode:
        data["options"]['testCode'] = testCode

    code, message, result = client.request('/repo/hash/query-efficiency-metric', data)
    return code, message, result





# 查询commit列表接口，返回结果是dict
# http://demo.meri.co/openapi/repo/commit/list
def repo_commit_dict(client, RepoId, page_size):
    final_result = {}
    result = [1]
    page = 1
    while len(result) != 0:
        code, message, result = client.request('/repo/commit/list', {
            "id": RepoId,
            "page": page,
            "pagesize": page_size
            })
        assert code == 200, message
        if len(result) != 0:
            for i in result:
                final_result[i['hash']] = i
            # print(f"获取到最新的 {page} 页面数据 数量为 {len(result)}")
        page += 1
    # print(f"代码库ID: {RepoId} 获取到的思码逸内commit数量是 {len(final_result)} ")

    # 按照创建时间倒序 排列commit 数据(最晚创建的commit在最前面，最早创建的commit在最后)
    final_result = {k: v for k, v in sorted(final_result.items(), key=lambda item: item[1]['authorTimestamp'], reverse=True)}
    return final_result



# 查询commit列表接口，返回结果是dict
# http://demo.meri.co/openapi/repo/commit/list
def get_repo_commit_list_v2(client, RepoId, page, pageSize, authorTimestampFrom, authorTimestampTo, commitTimestampFrom, commitTimestampTo):
    data = {}
    if RepoId:
        data["id"] = RepoId
    if page:
        data["page"] = page
    if pageSize:
        data["pageSize"] = pageSize
    if authorTimestampFrom:
        data["authorTimestampFrom"] = authorTimestampFrom
    if authorTimestampTo:
        data["authorTimestampTo"] = authorTimestampTo        
    if commitTimestampFrom:
        data["commitTimestampFrom"] = commitTimestampFrom
    if commitTimestampTo:
        data["commitTimestampTo"] = commitTimestampTo

    code, message, result = client.request('/repo/commit/list', data)

    return code, message, result



# 按照commit hash范围获取效率metric
# http://demo.meri.co/openapi/repo/branch/query-efficiency-metric
def get_efficiency_metric_by_commit_hash(client, selectRepoId, includePath, excludePath, startHash, endHash, unitOfTime, testCode):
    data = {}
    data["options"] = {}
    if selectRepoId:
        if type(selectRepoId) == str:
            data["repoId"] = selectRepoId
        if type(selectRepoId) == list:
            data["repoId"] = selectRepoId[0]
    if includePath:
        data["includePath"] = includePath
    if excludePath:
        data["excludePath"] = excludePath
    if startHash and endHash:
        data["options"]['startHash'] = startHash
        data["options"]['endHash'] = endHash
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode is not None:
        data["options"]['testCode'] = testCode

    data["options"]['selectColumns'] = [
        'commit_num', 'function_num', 'loc', 'loc_add_line', 'loc_delete_line',
        'share_loc', 'developer_num', 'dev_equivalent', 'dev_value',
        'dev_value_robustness', 'dev_equivalent_every_developer'
    ]

    print(f"Requesting efficiency metrics for repo: {selectRepoId}, from {startHash} to {endHash}")

    code, message, result = client.request('/repo/branch/query-efficiency-metric', data)

    return code, message, result


# 查询贡献者的质量报表
# http://demo.meri.co/openapi/repo/query-quality-metrics-graph-for-developers
def query_quality_metrics_graph_for_developers(client, recentPeriod_counts, recentPeriod_unit, timeRange_of_start, timeRange_of_end, records_type, records_id, repoIds, contributors):
    data = {}

    if recentPeriod_counts or recentPeriod_unit:
        data["recentPeriod"] = {}
        if recentPeriod_counts:
            data["recentPeriod"]["counts"] = int(recentPeriod_counts)
        if recentPeriod_unit:
            data["recentPeriod"]["unit"] = recentPeriod_unit

    if timeRange_of_start or timeRange_of_end:
        data["timeRange"] = []
        if timeRange_of_start:
            data["timeRange"].append(timeRange_of_start)
        if timeRange_of_end:
            data["timeRange"].append(timeRange_of_end)

    if records_type or records_id:
        data["records"] = []
        data["records"].append({})
        if records_type:
            data["records"][0]["type"] = records_type
        if records_id:
            data["records"][0]["id"] = records_id
        if repoIds:
            data["records"][0]["repoIds"] = repoIds
        if contributors:
            data["records"][0]["contributors"] = contributors

    code, message, result = client.request('/repo/query-quality-metrics-graph-for-developers', data)

    assert code == 200, message
    return result


#[Beta]获取 commit 变更函数
#http://demo.meri.co/openapi/repo/commit/get-changes-function
def repo_commit_get_changes_function(client, RepoId, commit_hash):
    data = {}
    data["id"] = RepoId
    data["hash"] = commit_hash
    data["pageSize"] = 1000
    data["current"] = 1 # 这里测试有点儿BUG, 后面修复BUG之后, 代码还要改下
    code, message, result = client.request('/repo/commit/get-changes-function', data)

    assert code == 200, message
    return result





# Project

# 创建项目
def project_add(client, project_add_dict):
    # print(f"project_add_dict = {project_add_dict}")
    data = {}
    data["name"] = project_add_dict["name"]
    data["description"] = project_add_dict["description"]
    data["parentProjectId"] = project_add_dict["parentProjectId"]
    if project_add_dict["logo"]:
        data["logo"] = project_add_dict["logo"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/add', data)

    return code, message, result



# 更新项目
def project_update(client, project_update_dict):
    # print(f"project_update_dict = {project_update_dict}")
    data = {}
    data["id"] = project_update_dict["id"]
    data["name"] = project_update_dict["name"]
    if project_update_dict["description"]:
        data["description"] = project_update_dict["description"]
    else:
        None
    if project_update_dict["logo_url"]:
        data["logo_url"] = project_update_dict["logo_url"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/update', data)

    return code, message, result



# 删除项目
def project_delete(client, project_delete_dict):
    # print(f"project_delete_dict = {project_delete_dict}")
    data = {}
    data["id"] = project_delete_dict["id"]

    # print(f"data = {data}")
    code, message, result = client.request('/project/delete', data)

    return code, message, result



# 移动项目
def project_move(client, project_move_dict):
    # print(f"project_move_dict = {project_move_dict}")
    data = {}
    data["projectId"] = project_move_dict["source_project_id"]
    if project_move_dict["target_project_id"]:
        data["parentId"] = project_move_dict["target_project_id"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/move-project', data)

    return code, message, result



# 添加项目成员
def project_add_member(client, project_add_member):
    # print(f"project_add_member = {project_add_member}")
    data = {}
    data["projectId"] = project_add_member["项目ID"]
    if project_add_member["账户ID列表"] or project_add_member["账户ID列表"] == []:
        data["accountIds"] = project_add_member["账户ID列表"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/add-member', data)

    return code, message, result



# 删除项目成员
def project_remove_member(client, project_remove_member):
    # print(f"project_remove_member = {project_remove_member}")
    data = {}
    data["projectId"] = project_remove_member["项目ID"]
    if project_remove_member["账户ID列表"] or project_remove_member["账户ID列表"] == []:
        data["accountIds"] = project_remove_member["账户ID列表"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/remove-member', data)

    return code, message, result



# 列出项目成员
def project_list_member(client, project_id):
    # print(f"project_id = {project_id}")
    data = {}
    data["projectId"] = project_id

    # print(f"data = {data}")
    code, message, result = client.request('/project/list-member', data)

    return code, message, result



# 查询项目中的代码库列表
def project_list_repo(client, selectGroupId):
    code, message, result = client.request('/project/list-repo', {
        "projectId": selectGroupId,
    })
    assert code == 200, message
    return result



# 移动代码库到另一个项目
def project_move_repo(client, project_move_repo):
    data = {}
    data["repoId"] = project_move_repo["source_repo_id"]
    if project_move_repo["target_project_id"]:
        data["projectId"] = project_move_repo["target_project_id"]
    else:
        None

    code, message, result = client.request('/project/move-repo', data)

    return code, message, result



# 将一个代码库移出项目
def project_remove_repo(client, project_remove_repo):
    data = {}
    data["repoId"] = project_remove_repo["source_repo_id"]
    if project_remove_repo["target_project_id"]:
        data["projectId"] = project_remove_repo["target_project_id"]
    else:
        None

    code, message, result = client.request('/project/remove-repo', data)

    return code, message, result



# 查询项目及其全部后代节点项目的贡献者邮箱
def project_get_emails(client, project_id):
    # print(f"project_id = {project_id}")
    data = {}
    data["id"] = project_id

    # print(f"data = {data}")
    code, message, result = client.request('/project/get-emails', data)

    return code, message, result



# 查询项目查询授权情况
def project_query_auth(client, project_id):
    # print(f"project_id = {project_id}")
    data = {}
    data["id"] = project_id

    # print(f"data = {data}")
    code, message, result = client.request('/project/query-auth', data)

    return code, message, result



# 更新项目授权情况
def project_update_auth(client, project_update_auth):
    # print(f"project_update_auth = {project_update_auth}")
    data = {}
    data["id"] = project_update_auth['project_id']
    if project_update_auth["accountIds"]:
        if project_update_auth["accountIds"] == ['清空']:
            data["accountIds"] = []
        else:
            data["accountIds"] = project_update_auth["accountIds"]
    else:
        None

    if project_update_auth["teamIds"]:
        if project_update_auth["teamIds"] == ['清空']:
            data["teamIds"] = []
        else:
            data["teamIds"] = project_update_auth["teamIds"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/project/update-auth', data)

    return code, message, result



# 获取项目效率稳定性数据
def get_project_query_stability(client, project_query_stability):
    # print(f"project_query_stability = {project_query_stability}")
    data = {}
    data["ids"] = project_query_stability['project_id_list']
    data["startDate"] = project_query_stability['start_date']
    data["endDate"] = project_query_stability['end_date']
    data["unitOfTime"] = project_query_stability['unit_of_time']
    data["unitNumber"] = project_query_stability['unit_of_number']
    data["timezoneName"] = project_query_stability['time_zone_Name']

    # print(f"data = {data}")
    code, message, result = client.request('/project/query-stability', data)

    return code, message, result






# 以项目组聚合获取效率metric
def get_efficiency_metric_by_project_id(client, selectGroupIds, start_date, end_date, unitOfTime, testCode):
    data = {}
    data["options"] = {}
    if selectGroupIds:
        if type(selectGroupIds) == str:
            data["projectIds"] = [selectGroupIds]
        if type(selectGroupIds) == list:
            data["projectIds"] = selectGroupIds
    if start_date or end_date:
        data["options"]['authorTime'] = {}
        data["options"]['authorTime']['startDate'] = start_date
        data["options"]['authorTime']['endDate'] = end_date
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode == True or testCode == False:
        data["options"]['testCode'] = testCode

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('commit_num')                     # 提交数
    data["options"]['selectColumns'].append('function_num')                   # 函数个数
    data["options"]['selectColumns'].append('loc')                            # 代码行数
    data["options"]['selectColumns'].append('loc_add_line')                   # 新增代码行数
    data["options"]['selectColumns'].append('loc_delete_line')                # 删除代码行数
    data["options"]['selectColumns'].append('share_loc')                      # 代码行数占比
    data["options"]['selectColumns'].append('developer_num')                  # 开发者人数
    data["options"]['selectColumns'].append('dev_equivalent')                 # 开发当量
    data["options"]['selectColumns'].append('dev_value')                      # 开发价值
    data["options"]['selectColumns'].append('dev_value_robustness')           # 开发价值鲁棒性（开发者开发价值贡献是否均衡）
    data["options"]['selectColumns'].append('dev_equivalent_every_developer') # 开发者平均开发当量
    # 代码行数在查询测试/非测试代码（包含testCode参数），或过滤文件路径（包含projectFolderFilter参数）时，
    # 行数计算是基于函数修改前后文本的对比，不是直接从git commit diff获取的原始增删行数，与commit粒度的查询结果会存在差异。


    code, message, result = client.request('/project/query-efficiency-metric', data)
    return code, message, result





# 以项目组聚合获取质量metric
def get_quality_metric_by_project_id(client, selectGroupIds, dateQuery):
    data = {}
    if selectGroupIds:
        if type(selectGroupIds) == str:
            data["projectIds"] = [selectGroupIds]
        if type(selectGroupIds) == list:
            data["projectIds"] = selectGroupIds

    data["options"] = {}
    data["options"]['selectColumns'] = []

    data["options"]['selectColumns'].append('doc_coverage_function_num')
    data["options"]['selectColumns'].append('doc_coverage_total_function_num')
    data["options"]['selectColumns'].append('doc_coverage')
    data["options"]['selectColumns'].append('static_test_coverage_function_num')
    data["options"]['selectColumns'].append('static_test_coverage_total_function_num')
    data["options"]['selectColumns'].append('static_test_coverage')

    data["options"]['selectColumns'].append('issue_blocker_num')
    data["options"]['selectColumns'].append('issue_critical_num')
    data["options"]['selectColumns'].append('issue_info_num')
    data["options"]['selectColumns'].append('issue_major_num')
    data["options"]['selectColumns'].append('issue_minor_num')
    data["options"]['selectColumns'].append('issue_num')

    data["options"]['selectColumns'].append('issue_rate')
    data["options"]['selectColumns'].append('severe_issue_rate')
    data["options"]['selectColumns'].append('weighted_issue_rate')

    # 开发者影响力（某开发者的函数被其他人使用的次数，此指标只在以开发者维度聚合时有意义）
    # data["options"]['selectColumns'].append('function_depend')
    data["options"]['selectColumns'].append('ccg_snapshot_function_num')
    data["options"]['selectColumns'].append('duplicate_function_num')
    data["options"]['selectColumns'].append('dryness')
    data["options"]['selectColumns'].append('modularity')
    data["options"]['selectColumns'].append('cyclomatic_total')
    data["options"]['selectColumns'].append('cyclomatic_total_every_function')
    data["options"]['selectColumns'].append('cyclomatic_total_every_1k_dev_eq')

    data["options"]['selectColumns'].append('techtag')

    if dateQuery["recentPeriod"]:
        data["dateQuery"] = {}
        if dateQuery["recentPeriod"]["counts"] and dateQuery["recentPeriod"]["unit"]:
            data["dateQuery"]["recentPeriod"] = dateQuery["recentPeriod"]
        if dateQuery["since"]:
            data["dateQuery"]["since"] = dateQuery["since"]
        if dateQuery["until"]:
            data["dateQuery"]["until"] = dateQuery["until"]

    code, message, result = client.request('/project/query-quality-metric', data)
    assert code == 200, message
    return result



# 查询项目人力专注度
def get_project_query_focusness(client, query_type, start_date, end_date, execute_id):
    data = {}
    if query_type == 'repo' or query_type == '':
        data["repoId"] = execute_id
    else:
        data["projectId"] = execute_id

    if start_date:
        data["since"] = start_date

    if end_date:
        data["until"] = end_date

    code, message, result = client.request('/project/query-focusness', data)
    # assert code == 200, message
    return code, message, result


# 查询项目代码质量问题
def get_project_list_issues(client, projectId, page, pageSize):
    data = {}
    if projectId:
        data["id"] = projectId # 项目ID

    data["page"] = page # 页数
    data["pageSize"] = pageSize # 返回记录数: integer

    code, message, result = client.request('/project/list-issues', data)

    # print(f"code = {code}")
    # print(f"message = {message}")
    # print(f"result = {result}")

    return code, message, result



# 查询效率质量综合排行,
def get_query_overall_ranking(client, query_type, execute_id, contributors, limit, offset):
    data = {}
    if query_type == 'repo' or query_type == '':
        data["repoIds"] = execute_id
    else:
        data["projectId"] = execute_id

    if contributors:
        data["contributors"] = contributors

    if limit:
        data["limit"] = limit

    if offset:
        data["offset"] = offset

    code, message, result = client.request('/project/query-overall-ranking', data)
    # print(f"code = {code}")
    # print(f"message = {message}")
    # print(f"result = {result}")
    # assert code == 200, message
    return code, message, result



# 以项目组聚合获取双周


# 根据项目id，查询项目中的代码库列表，V2新接口
def get_list_project_by_group_id(client, selectGroupId):
    code, message, result = client.request('/project/list-repo', {
        "projectId": selectGroupId,
    })
    assert code == 200, message
    return result



# 根据代码库id，查询代码库的commit的列表，V2新接口
# 这里API接口还有两个传参page 和 pageSize，但是如果不传递的话，也可以实现page=1，pageSize=100000，一般情况下可以覆盖绝大多数代码库
def get_commit_list_by_code_base_id_with_page(client, case_base_id, authorTimestampFrom, authorTimestampTo, page, pageSize):
    if authorTimestampFrom and authorTimestampTo:
        request_hash = {
            "id": case_base_id,
            "authorTimestampFrom": authorTimestampFrom,
            "authorTimestampTo": authorTimestampTo,
            "page": page,
            "pageSize": pageSize
            }
    else:
        request_hash = {
            "id": case_base_id,
            "page": page,
            "pageSize": pageSize
            }
    code, message, result = client.request('/repo/commit/list', request_hash)
    assert code == 200, message
    return result



# 根据代码库id，查询代码库的commit的列表，V2新接口
# 这里API接口还有两个传参page 和 pageSize，但是如果不传递的话，也可以实现page=1，pageSize=100000，一般情况下可以覆盖绝大多数代码库
def get_commit_list_by_code_base_id(client, case_base_id, authorTimestampFrom, authorTimestampTo):
    if authorTimestampFrom and authorTimestampTo:
        request_hash = {
            "id": case_base_id,
            "authorTimestampFrom": authorTimestampFrom,
            "authorTimestampTo": authorTimestampTo
            }
    else:
        request_hash = {"id": case_base_id}
    code, message, result = client.request('/repo/commit/list', request_hash)
    assert code == 200, message
    return result




# 查询邮箱
# http://demo.meri.co/openapi/repo/get-emails
def get_emails_by_repo_id(client, repo_id):

    request_hash = {"id": repo_id}

    code, message, result = client.request('/repo/get-emails', request_hash)
    assert code == 200, message
    return result


# 查询代码库的 techtag 和对应的 packages
# http://demo.meri.co/openapi/repo/techtag-packages
def get_repo_techtag_packages(client, data):

    request_hash = {}
    request_hash['format'] = data['format']
    request_hash['repoIds'] = data['repoIds']

    code, message, result = client.request('/repo/techtag-packages', request_hash)
    assert code == 200, message
    return result


# 获取所有项目信息，V2新接口
def get_all_group_id(client):
    code, message, result = client.request('/project/list', {})
    assert code == 200, message
    return result



# 获取所有项目信息，V2新接口
def get_all_project_id(client):
    code, message, result = client.request('/project/list', {})
    assert code == 200, message
    return result


# 获取所有项目信息，V2新接口
def get_project_list(client):
    code, message, result = client.request('/project/list', {})
    assert code == 200, message
    return result



# 获取所有项目dict
def get_all_project_dict(client):
    project_list = get_project_list(client)
    # print(f"project_list = {project_list}")
    project_dict = {project['id']: project for project in project_list}
    return project_dict



# 获取所有项目的id_name dict
def get_all_project_id_name(all_project_dict):
    result = {}
    for key, value in all_project_dict.items():
        result[value['id']] = value['name']

    return result



# 获取根项目dict
def get_root_project_dict(all_project_dict):
    first_level_project_dict = {}
    for index, i in enumerate(all_project_dict.items()):
        if i[1]['parentId'] == None:
            first_level_project_dict[i[1]['id']] = {}
            first_level_project_dict[i[1]['id']]['id'] = i[1]['id']
            first_level_project_dict[i[1]['id']]['name'] = i[1]['name']
            first_level_project_dict[i[1]['id']]['parentId'] = i[1]['parentId']
    # print(f"first_level_project_dict = {first_level_project_dict}")
    return first_level_project_dict



# 获取根项目ID
def get_root_project_id(root_project_dict):
    root_project_id = list(root_project_dict.keys())[0]
    return root_project_id



# For Team

# 创建团队
def team_add(client, team_add_dict):
    # print(f"team_add_dict = {team_add_dict}")
    data = {}
    data["name"] = team_add_dict["name"]
    data["parentId"] = team_add_dict["parentTeamId"]
    # print(f"data = {data}")
    code, message, result = client.request('/team/add', data)

    return code, message, result



# 更新团队
def team_update(client, team_update_dict):
    # print(f"team_update_dict = {team_update_dict}")
    data = {}
    data["id"] = team_update_dict["id"]
    if team_update_dict["name"]:
        data["name"] = team_update_dict["name"]
    else:
        None
    if team_update_dict["parentId"]:
        data["parentId"] = team_update_dict["parentId"]
    else:
        None

    # print(f"data = {data}")
    code, message, result = client.request('/team/update', data)

    return code, message, result



# 删除团队
def team_delete(client, team_delete_dict):
    # print(f"team_delete_dict = {team_delete_dict}")
    data = {}
    data["teamId"] = team_delete_dict["id"]

    # print(f"data = {data}")
    code, message, result = client.request('/team/delete', data)

    return code, message, result



# 获取团队成员列表，V2接口
# http://demo.meri.co/openapi/team/members
def get_team_members(client, teamId, offset, limit, subTeam):
    # print(f"teamId = {teamId}")
    # print(f"offset = {offset}")
    # print(f"limit = {limit}")
    # print(f"subTeam = {subTeam}")
    data = {}
    data["teamId"] = teamId
    data["offset"] = offset
    data["limit"] = limit
    data["subTeam"] = subTeam
    # print(f"data = {data}")
    code, message, result = client.request('/team/members', data)

    return code, message, result



# 获取团队列表，V2接口
def get_all_team_id(client):
    code, message, result = client.request('/team/list', {})
    assert code == 200, message
    return result



# 获取团队维度聚合获取质量metric
def get_quality_metric_by_team_id(client, selectTeamIds):
    data = {}
    if selectTeamIds:
        if type(selectTeamIds) == str:
            data["teamIds"] = [selectTeamIds]
        if type(selectTeamIds) == list:
            data["teamIds"] = selectTeamIds

    data["options"] = {}
    data["options"]['selectColumns'] = []

    data["options"]['selectColumns'].append('doc_coverage_function_num')
    data["options"]['selectColumns'].append('doc_coverage_total_function_num')
    data["options"]['selectColumns'].append('doc_coverage')
    data["options"]['selectColumns'].append('static_test_coverage_function_num')
    data["options"]['selectColumns'].append('static_test_coverage_total_function_num')
    data["options"]['selectColumns'].append('static_test_coverage')

    data["options"]['selectColumns'].append('issue_blocker_num')
    data["options"]['selectColumns'].append('issue_critical_num')
    data["options"]['selectColumns'].append('issue_info_num')
    data["options"]['selectColumns'].append('issue_major_num')
    data["options"]['selectColumns'].append('issue_minor_num')
    data["options"]['selectColumns'].append('issue_num')

    data["options"]['selectColumns'].append('issue_rate')
    data["options"]['selectColumns'].append('severe_issue_rate')
    data["options"]['selectColumns'].append('weighted_issue_rate')

    # 开发者影响力（某开发者的函数被其他人使用的次数，此指标只在以开发者维度聚合时有意义）
    # data["options"]['selectColumns'].append('function_depend')
    data["options"]['selectColumns'].append('ccg_snapshot_function_num')
    data["options"]['selectColumns'].append('duplicate_function_num')
    data["options"]['selectColumns'].append('dryness')
    data["options"]['selectColumns'].append('modularity')
    data["options"]['selectColumns'].append('cyclomatic_total')
    data["options"]['selectColumns'].append('cyclomatic_total_every_function')
    data["options"]['selectColumns'].append('cyclomatic_total_every_1k_dev_eq')

    data["options"]['selectColumns'].append('techtag')


    code, message, result = client.request('/team/query-quality-metric', data)
    assert code == 200, message
    return result




# 获取团队维度聚合获取效率metric
def get_efficiency_metric_by_team_id(client, selectTeamIds, start_date, end_date, unitOfTime, testCode):
    data = {}
    data["options"] = {}
    if selectTeamIds:
        if type(selectTeamIds) == str:
            data["teamIds"] = [selectTeamIds]
        if type(selectTeamIds) == list:
            data["teamIds"] = selectTeamIds
    if start_date or end_date:
        data["options"]['authorTime'] = {}
        data["options"]['authorTime']['startDate'] = start_date
        data["options"]['authorTime']['endDate'] = end_date
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime
    if testCode == True or testCode == False:
        data["options"]['testCode'] = testCode

    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('commit_num')                     # 提交数
    data["options"]['selectColumns'].append('function_num')                   # 函数个数
    data["options"]['selectColumns'].append('loc')                            # 代码行数
    data["options"]['selectColumns'].append('loc_add_line')                   # 新增代码行数
    data["options"]['selectColumns'].append('loc_delete_line')                # 删除代码行数
    data["options"]['selectColumns'].append('share_loc')                      # 代码行数占比
    data["options"]['selectColumns'].append('developer_num')                  # 开发者人数
    data["options"]['selectColumns'].append('dev_equivalent')                 # 开发当量
    data["options"]['selectColumns'].append('dev_value')                      # 开发价值
    data["options"]['selectColumns'].append('dev_value_robustness')           # 开发价值鲁棒性（开发者开发价值贡献是否均衡）
    data["options"]['selectColumns'].append('dev_equivalent_every_developer') # 开发者平均开发当量
    # 代码行数在查询测试/非测试代码（包含testCode参数），或过滤文件路径（包含projectFolderFilter参数）时，
    # 行数计算是基于函数修改前后文本的对比，不是直接从git commit diff获取的原始增删行数，与commit粒度的查询结果会存在差异。
    code, message, result = client.request('/team/query-efficiency-metric', data)

    assert code == 200, message
    return result



# For Role
# 获取角色列表，V2接口
def get_all_role_id(client):
    code, message, result = client.request('/role/list', {})
    assert code == 200, message
    return result



# 查询项目的贡献者邮箱
def get_all_emails_by_project_id(client, selectGroupId):
    code, message, result = client.request('/project/get-emails', {
        "id": selectGroupId,
    })
    assert code == 200, message
    return result



# 获取开发者维度聚合效率metric
# http://demo.meri.co/openapi/developer/query-efficiency-metric
def get_efficiency_metric_by_developer_email(client, primaryEmailStrs, startDate, endDate, unitOfTime, repoId, selectGroupIds, testCode):
    data = {}
    if primaryEmailStrs:
        if type(primaryEmailStrs) == str:
            data["primaryEmailStrs"] = [primaryEmailStrs]
        if type(primaryEmailStrs) == list:
            data["primaryEmailStrs"] = primaryEmailStrs

    data["options"] = {}
    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('dev_equivalent')
    data["options"]['selectColumns'].append('commit_num')
    data["options"]['selectColumns'].append('function_num')
    data["options"]['selectColumns'].append('loc')
    data["options"]['selectColumns'].append('loc_add_line')
    data["options"]['selectColumns'].append('loc_delete_line')
    data["options"]['selectColumns'].append('share_loc')
    data["options"]['selectColumns'].append('developer_num')
    data["options"]['selectColumns'].append('dev_equivalent')
    data["options"]['selectColumns'].append('dev_value')
    data["options"]['selectColumns'].append('dev_value_robustness')
    data["options"]['selectColumns'].append('dev_equivalent_every_developer')
    data["options"]['authorTime'] = startDate and endDate and{"startDate":startDate,"endDate":endDate} or None
    if unitOfTime:
        data["options"]['unitOfTime'] = unitOfTime

    if repoId:
        data["options"]['repoId'] = repoId

    if selectGroupIds:
        data["options"]["projectId"] = selectGroupIds

    if testCode == True or testCode == False:
        data["options"]['testCode'] = testCode

    code, message, result = client.request('/developer/query-efficiency-metric', data)
    assert code == 200, message
    return result



# 获取个人技能标签数据
# http://demo.meri.co/openapi/developer/tech-tag
def get_tech_tag_by_developer_email(client, primaryEmailStrs, repoId, projectId):
    data = {}
    if primaryEmailStrs:
        if type(primaryEmailStrs) == str:
            data["primaryEmailStrs"] = [primaryEmailStrs]
        if type(primaryEmailStrs) == list:
            data["primaryEmailStrs"] = primaryEmailStrs
    if repoId:
        data['repoId'] = repoId

    if projectId:
        data["projectId"] = projectId

    code, message, result = client.request('/developer/tech-tag', data)
    assert code == 200, message
    return result




# 07_TestFileConfig
# 01_列出测试代码路径配置
# http://demo.meri.co/openapi/test-file-config/list-configs
def get_test_file_config_list_configs(client):
    code, message, result = client.request('/test-file-config/list-configs', {})
    assert code == 200, message
    return result




# 02_修改测试代码路径配置
# http://demo.meri.co/openapi/test-file-config/update-config
def test_file_config_update_configs(client, configs_dict):
    data = {}
    if configs_dict['配置ID']:
        data['id'] = configs_dict['配置ID']
    if configs_dict['配置正则表达']:
        data['regex'] = configs_dict['配置正则表达']

    code, message, result = client.request('/test-file-config/update-config', data)
    # assert code == 200, message
    return code, message, result


# 08_System
# http://demo.meri.co/openapi/system/query-ae-version
def get_system_query_ae_version(client):
    code, message, result = client.request('/system/query-ae-version', {})
    assert code == 200, message
    return result




# 09_Industry
# 同行对比：人均当量趋势
# http://demo.meri.co/openapi/industry/dev-eq-per-capita
def get_industry_dev_eq_per_capita(client, pattern_id, idType, recentPeriod_counts, recentPeriod_unit, start_date, end_date, unitNumber):
    data = {}
    if pattern_id:
        data['id'] = pattern_id
    if idType:
        data['idType'] = idType
    data['dateQuery'] = {}
    if recentPeriod_counts and recentPeriod_unit:
        data['dateQuery']['recentPeriod'] = {}
        data['dateQuery']['recentPeriod']['counts'] = recentPeriod_counts
        data['dateQuery']['recentPeriod']['unit'] = recentPeriod_unit
    if start_date and end_date:
        data['dateQuery']['dateRange'] = []
        data['dateQuery']['dateRange'].append(start_date)
        data['dateQuery']['dateRange'].append(end_date)
    if unitNumber:
        data['unitNumber'] = unitNumber
    code, message, result = client.request('/industry/dev-eq-per-capita', data)
    assert code == 200, message
    return result



# 同行对比：新增当量趋势
# http://demo.meri.co/openapi/industry/new-dev-eq
def get_industry_new_dev_eq(client, pattern_id, idType, recentPeriod_counts, recentPeriod_unit, start_date, end_date, unitNumber):
    data = {}
    if pattern_id:
        data['id'] = pattern_id
    if idType:
        data['idType'] = idType
    data['dateQuery'] = {}
    if recentPeriod_counts and recentPeriod_unit:
        data['dateQuery']['recentPeriod'] = {}
        data['dateQuery']['recentPeriod']['counts'] = recentPeriod_counts
        data['dateQuery']['recentPeriod']['unit'] = recentPeriod_unit
    if start_date and end_date:
        data['dateQuery']['dateRange'] = []
        data['dateQuery']['dateRange'].append(start_date)
        data['dateQuery']['dateRange'].append(end_date)
    if unitNumber:
        data['unitNumber'] = unitNumber
    code, message, result = client.request('/industry/new-dev-eq', data)
    assert code == 200, message
    return result



# 同行对比：项目信息
# http://demo.meri.co/openapi/industry/info
def get_industry_info(client, pattern_id, idType, recentPeriod_counts, recentPeriod_unit, start_date, end_date):
    data = {}
    if pattern_id:
        data['id'] = pattern_id
    if idType:
        data['idType'] = idType
    data['dateQuery'] = {}
    if recentPeriod_counts and recentPeriod_unit:
        data['dateQuery']['recentPeriod'] = {}
        data['dateQuery']['recentPeriod']['counts'] = recentPeriod_counts
        data['dateQuery']['recentPeriod']['unit'] = recentPeriod_unit
    if start_date and end_date:
        data['dateQuery']['dateRange'] = []
        data['dateQuery']['dateRange'].append(start_date)
        data['dateQuery']['dateRange'].append(end_date)
    code, message, result = client.request('/industry/info', data)
    assert code == 200, message
    return result



# 行业质量
# http://demo.meri.co/openapi/industry/quality
def get_industry_quality(client, pattern_id, idType, metricType):
    data = {}
    if pattern_id:
        data['id'] = pattern_id
    if idType:
        data['idType'] = idType
    if metricType:
        data['metricType'] = metricType

    code, message, result = client.request('/industry/quality', data)
    assert code == 200, message
    return result



#10 SPrint
# 根据项目id，查询项目的sprint的列表，V2新接口
# http://demo.meri.co/openapi/project/list-sprints
def get_sprint_list_by_project_id_with_page(client, project_id, includingMetaData, page, pageSize):
    data = {}
    if project_id:
        data['projectId'] = project_id
    if includingMetaData:
        data['includingMetaData'] = includingMetaData
    if page:
        data['page'] = page
    if pageSize:
        data['pageSize'] = pageSize
    code, message, result = client.request('/project/list-sprints', data)
    assert code == 200, message
    return result



#10 SPrint
# 02_获取迭代中的事务列表
# http://demo.meri.co/openapi/project/sprint/list-issues
def get_issues_list_by_project_sprint_id(client, project_id, sprint_id, issue_field, issue_sort, issue_priority, issue_assigneeId, issue_status, issue_type, issueKeys):
    data = {}
    if project_id:
        data['projectId'] = project_id
    if sprint_id:
        data['sprintId'] = sprint_id
    if issue_field:
        data['field'] = issue_field
    if issue_sort:
        data['sort'] = issue_sort
    if issue_priority:
        data['priority'] = issue_priority
    if issue_assigneeId:
        data['assigneeId'] = issue_assigneeId
    if issue_status:
        data['status'] = issue_status
    if issue_type:
        data['type'] = issue_type
    if issueKeys:
        data['issueKeys'] = issueKeys
    code, message, result = client.request('project/sprint/list-issues', data)
    assert code == 200, message
    return result



# 11 IssueTracking
# http://demo.meri.co/openapi/project/issue-tracking/list-issues
def get_issue_list_by_project_id_with_page(client, project_id, issue_field_with_date, issue_sort, statusCategory, typeCategory, issue_status, issue_type, timeRangeType, startDate, endDate, issueKeys, page, pageSize):
    data = {}
    if project_id:
        data['projectId'] = project_id
    if issue_field_with_date:
        data['issue_field_with_date'] = issue_field_with_date
    if issue_sort:
        data['issue_sort'] = issue_sort
    if statusCategory:
        data['statusCategory'] = statusCategory
    if typeCategory:
        data['typeCategory'] = typeCategory
    if issue_status:
        data['issue_status'] = issue_status
    if issue_type:
        data['issue_type'] = issue_type
    if timeRangeType:
        data['timeRangeType'] = timeRangeType
    if startDate:
        data['startDate'] = startDate
    if endDate:
        data['endDate'] = endDate
    if issueKeys:
        data['issueKeys'] = issueKeys
    if page:
        data['page'] = page
    if pageSize:
        data['pageSize'] = pageSize
    code, message, result = client.request('/project/issue-tracking/list-issues', data)
    assert code == 200, message
    return result



# 11 IssueTracking
# 获取项目关联的事务统计
# http://demo.meri.co/openapi/project/issue-tracking/query-issue-stat
def get_issue_stat_by_project_id(client, projectId, issue_groupBy, timeRangeType, startDate, endDate):
    data = {}
    if projectId:
        data['projectId'] = projectId
    if issue_groupBy:
        data['groupBy'] = issue_groupBy
    if timeRangeType:
        data['timeRangeType'] = timeRangeType
    if startDate:
        data['startDate'] = startDate
    if endDate:
        data['endDate'] = endDate

    code, message, result = client.request('/project/issue-tracking/query-issue-stat', data)
    assert code == 200, message
    return result



# 11 IssueTracking
# 关联项目看板
# http://demo.meri.co/openapi/project/issue-tracking/link-board
def project_issue_tracking_link_board(client, board_dict):
    data = {}
    if board_dict['boardSourceType']:
        data['boardSourceType'] = board_dict['boardSourceType']
    if board_dict['sourceId']:
        data['sourceId'] = board_dict['sourceId']
    if board_dict['projectId']:
        data['projectId'] = board_dict['projectId']
    if board_dict['boardId']:
        data['boardId'] = board_dict['boardId']
    if board_dict['boardName']:
        data['boardName'] = board_dict['boardName']

    code, message, result = client.request('/project/issue-tracking/link-board', data)
    return code, message, result



# 11 IssueTracking
# 查询迭代表现项目千当量缺陷率指标趋势
# http://demo.meri.co/openapi/project/bug_per_k_dev_eq_trending
def get_project_bug_per_k_dev_eq_trending(client, projectIds, recentPeriod_counts, recentPeriod_unit, start_date, end_date, groupDimension):
    data = {}
    if projectIds:
        data['projectIds'] = projectIds
    data['dateQuery'] = {}
    if recentPeriod_counts and recentPeriod_unit:
        data['dateQuery']['recentPeriod'] = {}
        data['dateQuery']['recentPeriod']['counts'] = recentPeriod_counts
        data['dateQuery']['recentPeriod']['unit'] = recentPeriod_unit
    if start_date and end_date:
        data['dateQuery']['dateRange'] = []
        data['dateQuery']['dateRange'].append(start_date)
        data['dateQuery']['dateRange'].append(end_date)
    if groupDimension:
        data['groupDimension'] = groupDimension

    code, message, result = client.request('/project/bug_per_k_dev_eq_trending', data)
    return code, message, result



# 12 AspectMetric
# 查询切面数据
# http://demo.meri.co/openapi/query-aspect-metric
def query_aspect_metric(client, repoIds, developers, snapshotTime, pageSize, page):
    data = {}
    if repoIds:
        if type(repoIds) == str:
            data["repoIds"] = [repoIds]
        if type(repoIds) == list:
            data["repoIds"] = repoIds
    if developers:
        if type(developers) == str:
            data["developers"] = [developers]
        if type(developers) == list:
            data["developers"] = developers
    if snapshotTime:
        data['snapshotTime'] = snapshotTime
    if pageSize:
        data['pageSize'] = pageSize
    if page:
        data['page'] = page

    code, message, result = client.request('/query-aspect-metric', data)
    return code, message, result





# 代码库停止分析
# http://demo.meri.co/openapi/repo/terminate-analysis
def repo_terminate_analysis(client, RepoIdsList):
    data = {}
    if RepoIdsList:
        if type(RepoIdsList) == str:
            data["ids"] = [RepoIdsList]
        if type(RepoIdsList) == list:
            data["ids"] = RepoIdsList

    code, message, result = client.request('/repo/terminate-analysis', data)
    return code, message, result


# 代码库开始分析
# http://demo.meri.co/openapi/repo/start-analysis
def repo_start_analysis(client, repoId, RepoIdsList, isforceAnalyze):
    data = {}
    if repoId:
        data['id'] = repoId
    if RepoIdsList:
        data['ids'] = RepoIdsList
    if isforceAnalyze:
        data['forceAnalyze'] = isforceAnalyze

    code, message, result = client.request('/repo/start-analysis', data)
    return code, message, result



# 获取开发者参与的代码库
# http://demo.meri.co/openapi/developer/query-repos
def get_developer_query_repos(client, Email):
    code, message, result = client.request('/developer/query-repos', {
        "email": Email,
    })
    assert code == 200, message
    return result


# 修改代码库分析配置
# http://demo.meri.co/openapi/repo/set-analytics-setting
def set_analysis_setting_for_v2(client, RepoId, data):
    param_data = {}
    param_data['id'] = RepoId
    if data['singleBranch'] in [True, False]:
        param_data['singleBranch'] = data['singleBranch']
    if data['aspectAnalysis'] in [True, False]:
        param_data['aspectAnalysis'] = data['aspectAnalysis']
    if data['codeQualityAnalysis'] in [True, False]:
        param_data['codeQualityAnalysis'] = data['codeQualityAnalysis']
    if data['defaultRef']:
        param_data['defaultRef'] = data['defaultRef']
    if data['commitAfterTime']:
        param_data['commitAfterTime'] = data['commitAfterTime']
    if data['sysExcludedPaths']:
        param_data['sysExcludedPaths'] = data['sysExcludedPaths']
    if data['customGlobExcludedPaths']:
        param_data['customGlobExcludedPaths'] = data['customGlobExcludedPaths']
    if data['excludedCommitHashes']:
        param_data['excludedCommitHashes'] = data['excludedCommitHashes']
    if data['commitSlocLimit']:
        param_data['commitSlocLimit'] = data['commitSlocLimit']

    code, message, result = client.request('/repo/set-analytics-setting', param_data)
    return code, message, result



# 查询代码库的函数列表
# http://demo.meri.co/openapi/repo/get-functions
def repo_get_functions(client, repo_id, email, page, pageSize):
    data = {}
    if repo_id:
        data["id"] = repo_id
    if email:
        data["email"] = email
    data["page"] = page # 页数
    data["pageSize"] = pageSize # 返回记录数: integer
    code, message, result = client.request('/repo/get-functions', data)
    return code, message, result



# 查询函数详情
# http://demo.meri.co/openapi/repo/function-detail
def get_repo_function_detail(client, repo_id, page, pageSize, authorEmail, isTest, isTestCovered, isDocCovered, hasDuplication):
    isTest = judge_bool(isTest)
    isTestCovered = judge_bool(isTestCovered)
    isDocCovered = judge_bool(isDocCovered)
    hasDuplication = judge_bool(hasDuplication)
    data = {}
    if repo_id:
        data["repoId"] = repo_id
    if authorEmail:
        if type(authorEmail) == str:
            data["authorEmail"] = [authorEmail]
        if type(authorEmail) == list:
            data["authorEmail"] = authorEmail
    if isTest:
        data["isTest"] = isTest
    if isTestCovered:
        data["isTestCovered"] = isTestCovered
    if isDocCovered:
        data["isDocCovered"] = isDocCovered
    if hasDuplication:
        data["hasDuplication"] = hasDuplication
    data["page"] = page # 页数
    data["pageSize"] = pageSize # 返回记录数: integer
    code, message, result = client.request('/repo/function-detail', data)
    return code, message, result




def judge_bool(string_):
    if isinstance(string_, bool):
        bool_ = string_
    else:
        if string_ not in [None, '', [], ""]:
            string_ = string_.lower()
        if string_ == 'true':
            bool_ = True
        elif string_ == 'false':
            bool_ = False
        else:
            bool_ = ''
    # print(f"bool_ = {bool_}")
    return bool_


# 查询单个commit的变化详情
# http://demo.meri.co/openapi/repo/commit/get-changes
def repo_commit_get_changes(client, params_dict):

    code, message, result = client.request('/repo/commit/get-changes', params_dict)
    return code, message, result




# 更新代码库的git地址
# http://demo.meri.co/openapi/repo/renew-git-url
def repo_renew_git_url(client, repoId, newGitUrl):
    param_data = {}
    param_data['repoId'] = repoId
    param_data['newGitUrl'] = newGitUrl


    code, message, result = client.request('/repo/renew-git-url', param_data)
    return code, message, result




# 修改代码库授权
# http://demo.meri.co/openapi/repo/reauthorize
def repo_reauthorize(client, repoIds, authType, username, password, privateKey, secretId):
    param_data = {}
    if repoIds:
        if type(repoIds) == str:
            param_data["repoIds"] = [repoIds]
        if type(repoIds) == list:
            param_data["repoIds"] = repoIds
    if authType:
        param_data['authType'] = authType
    if username:
        param_data['username'] = username
    if password:
        param_data['password'] = password
    if privateKey:
        param_data['privateKey'] = privateKey
    if secretId:
        param_data['secretId'] = secretId


    code, message, result = client.request('/repo/reauthorize', param_data)
    return code, message, result






# 以开发者维度聚合获取质量metric
# http://demo.meri.co/openapi/developer/query-quality-metric
def get_developer_query_quality_metric(client, primaryEmailStrs, repoId, projectId):
    data = {}
    data["options"] = {}
    if primaryEmailStrs:
        data["primaryEmailStrs"] = primaryEmailStrs

    if repoId:
        data["options"]['repoId'] = repoId

    if projectId:
        data["options"]['projectId'] = projectId


    data["options"]['selectColumns'] = []
    data["options"]['selectColumns'].append('doc_coverage_function_num')                 # 有注释覆盖的函数个数
    data["options"]['selectColumns'].append('doc_coverage_total_function_num')           # 计算注释覆盖度的总函数个数（包含所有函数）
    data["options"]['selectColumns'].append('doc_coverage')                              # 注释覆盖度
    data["options"]['selectColumns'].append('static_test_coverage_function_num')         # 有测试覆盖的函数个数
    data["options"]['selectColumns'].append('static_test_coverage_total_function_num')   # 计算测试覆盖度的总函数个数（不包含匿名函数和测试函数的函数个数）
    data["options"]['selectColumns'].append('static_test_coverage')                      # 测试覆盖度

    data["options"]['selectColumns'].append('issue_blocker_num')                         # 阻塞问题数
    data["options"]['selectColumns'].append('issue_critical_num')                        # 严重问题数
    data["options"]['selectColumns'].append('issue_info_num')                            # 提醒问题数
    data["options"]['selectColumns'].append('issue_major_num')                           # 重要问题数
    data["options"]['selectColumns'].append('issue_minor_num')                           # 次要问题数
    data["options"]['selectColumns'].append('issue_num')                                 # 总代码问题数

    data["options"]['selectColumns'].append('issue_rate')                                # 代码问题比例（函数占比）
    data["options"]['selectColumns'].append('severe_issue_rate')                         # 重要问题密度: (issue_blocker_count + issue_critical_count) / total_dev_eq
    data["options"]['selectColumns'].append('weighted_issue_rate')                       # 加权问题数比例（函数占比）

    data["options"]['selectColumns'].append('function_depend')                           # 开发者影响力
    data["options"]['selectColumns'].append('ccg_snapshot_function_num')                 # 分析切面总函数个数
    data["options"]['selectColumns'].append('duplicate_function_num')                    # 重复函数个数
    data["options"]['selectColumns'].append('dryness')                                   # 代码不重复率
    data["options"]['selectColumns'].append('modularity')                                # 代码模块度
    data["options"]['selectColumns'].append('cyclomatic_total')                          # 全函数圈复杂度之和
    data["options"]['selectColumns'].append('cyclomatic_total_every_function')           # 平均每个函数圈复杂度
    data["options"]['selectColumns'].append('cyclomatic_total_every_1k_dev_eq')          # 平均每个千当量圈复杂度

    data["options"]['selectColumns'].append('techtag')                                   # 技能tag标签

    code, message, result = client.request('/developer/query-quality-metric', data)

    assert code == 200, message
    return result


# 获取开发者的开发当量不同编程语言的分布
# http://demo.meri.co/openapi/developer/dev-eq-lang-dist
def get_developer_dev_eq_lang_dist(client, developers, repoIds, since, until):
    data = {}
    if developers:
        if type(developers) == str:
            data["developers"] = [developers]
        if type(developers) == list:
            data["developers"] = developers
    if repoIds:
        if type(repoIds) == str:
            data["repoIds"] = [repoIds]
        if type(repoIds) == list:
            data["repoIds"] = repoIds
    if since:
        data["since"] = since
    if until:
        data["until"] = until

    code, message, result = client.request('/developer/dev-eq-lang-dist', data)

    assert code == 200, message
    return result


# 查询开发者排行榜
# http://demo.meri.co/openapi/developer/ranking
def get_developer_ranking(client, ranking_type, projectId, repoIds, contributors, limit):
    data = {}
    if ranking_type:
        data["rankingType"] = ranking_type
    if projectId:
        data["projectId"] = projectId
    if repoIds:
        if type(repoIds) == str:
            data["repoIds"] = [repoIds]
        if type(repoIds) == list:
            data["repoIds"] = repoIds
    if contributors:
        if type(contributors) == str:
            data["contributors"] = [contributors]
        if type(contributors) == list:
            data["contributors"] = contributors
    if limit:
        data["limit"] = limit

    code, message, result = client.request('/developer/ranking', data)

    assert code == 200, message
    return result


# 10_Sprint
# 创建导入csv issue的异步任务，需保证所有的 board 在 web 界面中已上传过一次，与项目已有关联
# http://demo.meri.co/openapi/project/sprint/import-csv
# csv_type(string): Enum: "issues" "issue_repo_commits"
# csvContent(string): csv文件内容
# connectionId(string): lake 连接 id
# incremental(string): 是否增量更新, 默认为false
# taskId(string): 任务id,如果指定且incremental为false, 则会覆盖该任务对应的看板的issue_repo_commits数据
def project_sprint_import_csv(client, request_body):

    code, message, result = client.request('/project/sprint/import-csv', request_body)
    return code, message, result



# 查询邮箱
# http://demo.meri.co/openapi/project/get-emails
def get_emails_by_project_id(client, project_id):

    request_hash = {"id": project_id}

    code, message, result = client.request('/project/get-emails', request_hash)
    assert code == 200, message
    return result


# 查询开发者排行榜
# http://demo.meri.co/openapi/developer/ranking
def get_developer_ranking(client, rankingType, projectId, repoIds, contributors, limit):
    data = {}
    data["rankingType"] = rankingType
    if projectId:
        data["projectId"] = projectId
    if repoIds:
        data["repoIds"] = repoIds
    data["contributors"] = contributors # 开发者Email列表: Array of strings
    data["limit"] = limit # 返回记录数: integer

    code, message, result = client.request('/developer/ranking', data)

    assert code == 200, message
    return result



# 根据标签组查询commit指标
# http://demo.meri.co/openapi/repo/commit/list-by-commit-label
def get_repo_commit_list_by_commit_label(client, repoIds, projectId, groupNames, labelValues, commitStartTime, commitEndTime, page, pageSize):
    data = {}
    if repoIds:
        data["repoIds"] = repoIds # 代码库ID列表，与项目ID二选一，都填写默认使用repoIds
    if projectId:
        data["projectId"] = projectId # 代码库所属项目ID，与代码库ID列表二选一，都填写默认使用repoIds
    if groupNames:
        data["groupNames"] = groupNames # 标签组名
    if labelValues:
        data["labelValues"] = labelValues # 标签
    if commitStartTime:
        data["commitStartTime"] = commitStartTime # Commit起始时间，例如：2022-04-01T07:35:54.413Z
    if commitEndTime:
        data["commitEndTime"] = commitEndTime # Commit截止时间，例如：2022-04-01T07:35:54.413Z

    data["page"] = page # 页数
    data["pageSize"] = pageSize # 返回记录数: integer

    code, message, result = client.request('/repo/commit/list-by-commit-label', data)

    assert code == 200, message
    return result


# 根据hash查询commit列表接口
# http://demo.meri.co/openapi/repo/commit/list-by-hash
def get_repo_commit_list_by_hash(client, queries):
    data = {}
    if queries:
        data["queries"] = queries # 查询条件，queries需要是一个list，并且其中的每一个元素，都是dict

    code, message, result = client.request('/repo/commit/list-by-hash', data)

    assert code == 200, message
    return result


# 查询代码问题
# http://demo.meri.co/openapi/code-issue/list
def get_code_issue_list(client, projectId, repoIds, startDate, endDate, authors, rules, issue_type, severity, filename, page, pageSize):
    data = {}
    if projectId:
        data["projectId"] = projectId # 代码库所属项目ID
    if repoIds:
        data["repoIds"] = repoIds # 代码库ID列表
    if startDate:
        data["startDate"] = startDate # Commit起始时间，例如：2022-04-01T07:35:54.413Z
    if endDate:
        data["endDate"] = endDate # Commit截止时间，例如：2022-04-01T07:35:54.413Z
    if authors:
        data["authors"] = authors # 提交者Email list
    if rules:
        data["rules"] = rules # 规则key
    if issue_type:
        data["type"] = issue_type # 问题类型 Items Enum: "PERFORMANCE" "VULNERABILITY" "SECURITY_HOTSPOT" "PORTABILITY" "BUG" "CODE_SMELL"
    if severity:
        data["severity"] = severity # 严重程度 Items Enum: "BLOCKER" "MINOR" "CRITICAL" "MAJOR" "INFO"
    if filename:
        data["filename"] = filename # 文件名（正则表达式匹配）

    data["page"] = page # 页数
    data["pageSize"] = pageSize # 返回记录数: integer

    code, message, result = client.request('/code-issue/list', data)

    assert code == 200, message
    return result


# 20_Jenkins
# 绑定Jenkins job到系统项目
# http://demo.meri.co/openapi/v2/app/data_source/jenkins
def bound_project_and_jenkins_job(client, project_and_jenkins_job):
    # print(f"project_and_jenkins_job = {project_and_jenkins_job}")
    data = {}
    data["projectId"] = project_and_jenkins_job["projectId"]
    data["sourceId"] = project_and_jenkins_job["sourceId"]
    if project_and_jenkins_job["jobNames"] or project_and_jenkins_job["jobNames"] == []:
        data["jobNames"] = project_and_jenkins_job["jobNames"]
    else:
        None
    # print(f"data = {data}")
    code, message, result = client.request('/v2/app/data_source/jenkins', data)
    # print(f"code = {code}")
    # print(f"message = {message}")
    # print(f"result = {result}")

    return code, message, result


# 21_SonarQube
# 绑定SonarQube项目到代码库
# http://demo.meri.co/openapi/v2/app/data_source/sonar
def bound_repo_and_sonarqube_project(client, repo_and_sonarqube_project):
    data = repo_and_sonarqube_project
    code, message, result = client.request('/v2/app/data_source/sonar', data)

    return code, message, result

