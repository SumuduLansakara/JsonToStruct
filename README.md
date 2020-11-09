[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/SumuduLansakara/JsonToStruct)](https://github.com/SumuduLansakara/JsonToStruct/blob/master/LICENSE)
[![Stars](https://img.shields.io/github/stars/SumuduLansakara/JsonToStruct?style=social)](https://github.com/SumuduLansakara/JsonToStruct/stargazers)
[![Watchers](https://img.shields.io/github/watchers/SumuduLansakara/JsonToStruct?style=social)](https://github.com/SumuduLansakara/JsonToStruct/watchers)


```
     ____                         ___________          _________  __                            __
    |    |  ______  ____    ____  \__    ___/  ____   /   _____/_/  |_ _______  __ __   ____  _/  |_
    |    | /  ___/ /  _ \  /    \   |    |    /  _ \  \_____  \ \   __\\_  __ \|  |  \_/ ___\ \   __\
/\__|    | \___ \ (  <_> )|   |  \  |    |   (  <_> ) /        \ |  |   |  | \/|  |  /\  \___  |  |
\________|/____  > \____/ |___|  /  |____|    \____/ /_______  / |__|   |__|   |____/  \___  > |__|
               \/              \/                            \/                            \/
```

Code generator for generating C++ type definitions from [JSON-schema](https://json-schema.org/) definitions

Following types are currently supported:
1. Simple type aliases
2. Array (vector) type aliases
3. Enums
4. Variant type aliases
5. Structures
6. Extended variants (special case of a struct, see below)

# Examples

1. Defining a simple type alias

> JSON schema definition
>    
>      "MyInt" : {
>          "type" "integer"
>      }
>
> Generated C++ code
>
>     using MyInt = int32_t;

2. Defining an array alias

> JSON schema definition
>    
>      "MyIntArray" : {
>          "type" "array",
>          "items": {
>               "type" : "integer"
>           }
>      }
>
> Generated C++ code
>
>     using MyIntArray = std::vector<int32_t>;

> NOTE:
> - Arrays are implemented as vectors as they are generally more convenient.

3. Defining an enum

> JSON schema definition
>    
>      "MyEnum" : {
>          "enum": [
>               "zero",
>               "one",
>               "two",
>               "three",
>           ]
>      }
>
> Generated C++ code
>
>     enum class MyEnum
>     {
>         zero = 0,
>         one = 1,
>         two = 2,
>         three = 3,
>     };

4. Defining a variant alias

> JSON schema definition
>    
>      "MyVariant" : {
>          "oneOf": [
>              {
>                  "type" : "integer"
>              },
>              {
>                  "type" : "string"
>              },
>              {
>                  "type" : "array",
>                  "items" : {
>                      "type": "boolean"
>                  }
>              },
>          ]
>      }
>
> Generated C++ code
>
>     using MyVariant = std::variant<int32_t, std::string, std::vector<bool>>;

5. Defining a C++ Structure

> JSON schema definition
>    
>      "MyStruct" : {
>          "type": "object",
>          "properties": {
>              "name": {
>                  "type" : "string"
>              },
>              "age": {
>                  "type" : "integer"
>              },
>              "scores": {
>                  "type" : "array",
>                  "items" : {
>                      "type": "integer"
>                  }
>              },
>          }
>      }
>
> Generated C++ code
>
>     struct MyStruct
>     {
>         std::string name;
>         int32_t age;
>         std::vector<int32_t> scores;
>     };

> **NOTE:**
> 
> - In addition to generating the struct members, the tool also generates two helper functions 
> to Serialize/Deserialize the object to/from json formatted string.

6. Defining an extended variants

> JSON schema definition
>    
>      "MyExtendedVariant" : {
>          "type": "object",
>          "@meta:cpp_type": "extended_variant",
>          "properties": {
>              "type": {
>                  "enum": ["int", "str", "array"]
>              },
>              "content": {
>                  "oneOf" : [
>                      {
>                          "type": "integer"
>                      },
>                      {
>                          "type": "string"
>                      },
>                      {
>                          "type": "array",
>                          "items": {
>                              "type": "number"
>                          }
>                      },
>                  ]
>              }
>          }
>      }
>
> Generated C++ code
>
>     struct MyStruct : std::variant<std::monostate, int32_t, std::string, std::vector<float>>
>     {
>         enum class Type : int32_t
>         {
>             int = 1,
>             str = 2,
>             array = 3,
>         };
>
>         template <Type MemberType, typename T>
>         void SetAs(T value) { emplace<static_cast<int32_t>(MemberType)>(value); }
>
>         template <Type MemberType>
>         [[nodiscard]] auto& GetAs() { return std::get<static_cast<int32_t>(MemberType)>(*this); }
>
>         template <Type MemberType>
>         [[nodiscard]] auto const& GetAs() const { return std::get<static_cast<int32_t>(MemberType)>(*this); }
>     };

> **NOTE:**
>
> - This is a struct that extend std::variant with defined list of variant member types.
> - This is introduced for convenience when using variants whose members need to be accessed
>   via an enum.
> - This type may not be needed in simple use cases.
> - Custom attribute `@meta:cpp_type` is used to distinguish this from a struct definition.
> - `std::monostate` type is implicitly added as the first variant member to make the variant 
>   default constructable without a significant overhead.

