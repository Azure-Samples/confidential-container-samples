using ContosoHR.Models;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;
using Microsoft.Data.SqlClient.AlwaysEncrypted.AzureKeyVaultProvider;
using Azure.Core;
using Azure.Identity;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace ContosoHR
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
            InitializeAzureKeyVaultProvider();
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddDbContext<ContosoHRContext>(options => 
                options.UseSqlServer(Configuration.GetConnectionString("ContosoHRDatabase")));
            services.AddControllers();
            services.AddRazorPages();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseRouting();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
                endpoints.MapRazorPages();
            });
        }

        private static Microsoft.IdentityModel.Clients.ActiveDirectory.ClientCredential _clientCredential;
        private void InitializeAzureKeyVaultProvider()
        {
            // Initialize the Azure Key Vault provider
            SqlColumnEncryptionAzureKeyVaultProvider sqlColumnEncryptionAzureKeyVaultProvider = 
                new SqlColumnEncryptionAzureKeyVaultProvider(KeyVaultAuthenticationCallback);
            SqlConnectionStringBuilder builder = new SqlConnectionStringBuilder(Configuration.GetConnectionString("ContosoHRDatabase"));
            if(builder.Authentication != SqlAuthenticationMethod.ActiveDirectoryManagedIdentity)
            {
                var clientId = Configuration.GetSection("KeyVault:clientId").Value;
                var secret = Configuration.GetSection("KeyVault:secret").Value;
                _clientCredential = new ClientCredential(clientId, secret);
            }
            // Register the Azure Key Vault provider
            SqlConnection.RegisterColumnEncryptionKeyStoreProviders(
                customProviders: new Dictionary<string, SqlColumnEncryptionKeyStoreProvider>(
                    capacity: 1, comparer: StringComparer.OrdinalIgnoreCase)
                {
                    {
                        SqlColumnEncryptionAzureKeyVaultProvider.ProviderName, sqlColumnEncryptionAzureKeyVaultProvider
                    }
                }
            );
        }

        // This callback method only applies to provide access to Azure Key Vault.
        // Follow tutorial and grant necessary privilges to managed identity used here:
        // https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/tutorial-windows-vm-access-nonaad
        public static async Task<string> KeyVaultAuthenticationCallback(string authority, string resource, string scope)
        {
            if (_clientCredential == null)
            {
                return await Task.Run(() => new ManagedIdentityCredential().GetToken(new TokenRequestContext(new string[] { "https://vault.azure.net/.default" })).Token);
            }
            else
            {
                var authContext = new AuthenticationContext(authority);
                AuthenticationResult result = await authContext.AcquireTokenAsync(resource, _clientCredential);
                if (result == null)
                {
                    throw new InvalidOperationException($"Failed to retrieve an access token for {resource}");
                }
                return result.AccessToken;
            }
        }
    }
}
