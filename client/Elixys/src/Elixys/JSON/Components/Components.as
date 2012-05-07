package Elixys.JSON.Components
{
	public class Components
	{
		/***
		 * Member functions
		 **/

		// Locates the class that corresponds to the given component
		public static function GetComponentClass(sComponentType:String):Class
		{
			for each (var pComponentClass:Class in m_pComponentTypes)
			{
				if (pComponentClass.COMPONENTTYPE == sComponentType)
				{
					return pComponentClass;
				}
			}
			throw new Error("Component type not found: " + sComponentType);
		}

		// Returns the skins for the component type
		public static function GetUpSkin(sComponentType:String):Class
		{
			return GetComponentClass(sComponentType).SKINUP;
		}
		public static function GetDownSkin(sComponentType:String):Class
		{
			return GetComponentClass(sComponentType).SKINDOWN;
		}
		public static function GetDisabledSkin(sComponentType:String):Class
		{
			return GetComponentClass(sComponentType).SKINDISABLED;
		}
		public static function GetActiveSkin(sComponentType:String):Class
		{
			return GetComponentClass(sComponentType).SKINACTIVE;
		}
		
		/***
		 * Member variables
		 **/
		
		protected static var m_pComponentTypes:Array = [ComponentAdd, ComponentCassette, ComponentComment, ComponentEluteF18,
			ComponentEvaporate, ComponentExternalAdd, ComponentInitialize, ComponentInstall, ComponentMix, ComponentMove,
			ComponentPrompt, ComponentReact, ComponentSummary, ComponentTransfer, ComponentTrapF18];
	}
}
